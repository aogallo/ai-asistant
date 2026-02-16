from dataclasses import dataclass

from app.schemas.accounting import (
    AccountCategory,
    AccountDefinition,
    AccountMappingRule,
    CashFlowDirection,
    ClassificationDecision,
    ClassificationRequest,
    ClassificationResponse,
    FeedbackRuleRequest,
    TransactionInput,
)


@dataclass
class _ScoredAccount:
    account: AccountDefinition
    score: float
    signals: list[str]


class AccountingClassifierService:
    _feedback_rules: list[AccountMappingRule] = []

    def classify_batch(
        self, request: ClassificationRequest
    ) -> ClassificationResponse:
        account_lookup = {
            a.code: a for a in request.chart_of_accounts if a.is_active
        }
        results: list[ClassificationDecision] = []

        merged_rules = [*self._feedback_rules, *request.mapping_rules]

        for transaction in request.transactions:
            decision = self._classify_transaction(
                transaction=transaction,
                accounts=account_lookup,
                rules=merged_rules,
                target_system=request.target_system,
            )
            results.append(decision)

        return ClassificationResponse(results=results)

    def register_feedback_rule(self, feedback: FeedbackRuleRequest) -> int:
        self._feedback_rules.append(
            AccountMappingRule(
                pattern=feedback.pattern,
                account_code=feedback.account_code,
                match_vendor_only=feedback.match_vendor_only,
            )
        )
        return len(self._feedback_rules)

    def _classify_transaction(
        self,
        transaction: TransactionInput,
        accounts: dict[str, AccountDefinition],
        rules: list[AccountMappingRule],
        target_system: str,
    ) -> ClassificationDecision:
        direction = transaction.direction or self._infer_direction(
            transaction.amount
        )
        desc = _normalize(transaction.description)
        vendor = _normalize(transaction.vendor or "")

        for rule in rules:
            pattern = _normalize(rule.pattern)
            if not pattern:
                continue
            in_vendor = pattern in vendor
            in_description = pattern in desc
            if in_vendor or (in_description and not rule.match_vendor_only):
                mapped = accounts.get(rule.account_code)
                if mapped:
                    signals = [
                        f"Mapping rule matched '{rule.pattern}' -> {mapped.code}"
                    ]
                    return self._build_decision(
                        transaction=transaction,
                        account=mapped,
                        confidence=0.98,
                        signals=signals,
                        target_system=target_system,
                    )

        best = self._score_accounts(
            transaction=transaction,
            accounts=accounts,
            direction=direction,
            normalized_description=desc,
            normalized_vendor=vendor,
        )

        if best is None:
            fallback_account = AccountDefinition(
                code="UNMAPPED",
                name="Unmapped Transactions",
                category=self._fallback_category(direction),
            )
            return self._build_decision(
                transaction=transaction,
                account=fallback_account,
                confidence=0.0,
                signals=["No matching account found in active chart"],
                target_system=target_system,
            )

        confidence = min(round(best.score, 2), 0.97)
        return self._build_decision(
            transaction=transaction,
            account=best.account,
            confidence=confidence,
            signals=best.signals,
            target_system=target_system,
        )

    def _score_accounts(
        self,
        transaction: TransactionInput,
        accounts: dict[str, AccountDefinition],
        direction: CashFlowDirection,
        normalized_description: str,
        normalized_vendor: str,
    ) -> _ScoredAccount | None:
        best: _ScoredAccount | None = None
        for account in accounts.values():
            score = 0.0
            signals: list[str] = []

            for vendor in account.vendors:
                norm_vendor = _normalize(vendor)
                if norm_vendor and norm_vendor == normalized_vendor:
                    score += 0.65
                    signals.append(f"Vendor exact match '{vendor}' (+0.65)")
                    break
                if norm_vendor and norm_vendor in normalized_vendor:
                    score += 0.4
                    signals.append(f"Vendor partial match '{vendor}' (+0.40)")

            keyword_hits = 0
            for keyword in account.keywords:
                norm_keyword = _normalize(keyword)
                if norm_keyword and norm_keyword in normalized_description:
                    keyword_hits += 1
                    signals.append(
                        f"Keyword '{keyword}' matched description (+0.15)"
                    )
            if keyword_hits > 0:
                score += min(0.45, 0.15 * keyword_hits)

            category_bias = self._direction_bias(
                category=account.category,
                direction=direction,
            )
            if category_bias > 0:
                score += category_bias
                signals.append(
                    f"Direction bias for {account.category.value} (+{category_bias:.2f})"
                )

            if best is None or score > best.score:
                best = _ScoredAccount(
                    account=account,
                    score=score,
                    signals=signals or ["Fallback: best available account"],
                )

        return best

    def _infer_direction(self, amount: float) -> CashFlowDirection:
        if amount > 0:
            return CashFlowDirection.INFLOW
        if amount < 0:
            return CashFlowDirection.OUTFLOW
        return CashFlowDirection.UNKNOWN

    def _direction_bias(
        self, category: AccountCategory, direction: CashFlowDirection
    ) -> float:
        if direction == CashFlowDirection.INFLOW:
            if category == AccountCategory.REVENUE:
                return 0.2
            if category == AccountCategory.LIABILITY:
                return 0.1
            if category == AccountCategory.ASSET:
                return 0.05
        if direction == CashFlowDirection.OUTFLOW:
            if category == AccountCategory.EXPENSE:
                return 0.2
            if category == AccountCategory.ASSET:
                return 0.1
            if category == AccountCategory.LIABILITY:
                return 0.05
        if direction == CashFlowDirection.TRANSFER:
            if category == AccountCategory.ASSET:
                return 0.2
            if category == AccountCategory.LIABILITY:
                return 0.1
        return 0.0

    def _fallback_category(
        self, direction: CashFlowDirection
    ) -> AccountCategory:
        if direction == CashFlowDirection.INFLOW:
            return AccountCategory.REVENUE
        if direction == CashFlowDirection.OUTFLOW:
            return AccountCategory.EXPENSE
        return AccountCategory.ASSET

    def _build_decision(
        self,
        transaction: TransactionInput,
        account: AccountDefinition,
        confidence: float,
        signals: list[str],
        target_system: str,
    ) -> ClassificationDecision:
        direction = transaction.direction or self._infer_direction(
            transaction.amount
        )
        dr_cr = "credit" if direction == CashFlowDirection.INFLOW else "debit"
        explanation = (
            f"Classified to {account.code} ({account.name}) as "
            f"{account.category.value} using {len(signals)} signal(s)."
        )
        integration_payload: dict[str, str | float] = {
            "system": target_system,
            "account_code": account.code,
            "account_name": account.name,
            "amount": abs(transaction.amount),
            "debit_or_credit": dr_cr,
            "memo": transaction.description,
        }
        return ClassificationDecision(
            transaction_id=transaction.transaction_id,
            transaction_type=account.category,
            account_code=account.code,
            account_name=account.name,
            confidence=confidence,
            explanation=explanation,
            matched_signals=signals,
            integration_payload=integration_payload,
        )


def _normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())
