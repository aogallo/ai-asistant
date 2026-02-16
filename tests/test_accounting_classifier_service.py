from app.schemas.accounting import (
    AccountCategory,
    AccountDefinition,
    ClassificationRequest,
    FeedbackRuleRequest,
    TransactionInput,
)
from app.services.accounting_classifier_service import (
    AccountingClassifierService,
)


def _chart() -> list[AccountDefinition]:
    return [
        AccountDefinition(
            code="4000",
            name="Product Revenue",
            category=AccountCategory.REVENUE,
            keywords=["subscription", "sale", "plan"],
            vendors=[],
        ),
        AccountDefinition(
            code="6100",
            name="Software Expense",
            category=AccountCategory.EXPENSE,
            keywords=["hosting", "cloud", "api", "license"],
            vendors=["aws", "openai"],
        ),
        AccountDefinition(
            code="1100",
            name="Cash",
            category=AccountCategory.ASSET,
            keywords=["bank transfer"],
            vendors=[],
        ),
    ]


def test_classifies_transaction_type_and_account_code():
    service = AccountingClassifierService()
    service._feedback_rules = []
    request = ClassificationRequest(
        transactions=[
            TransactionInput(
                transaction_id="t-1",
                description="Monthly cloud hosting invoice",
                vendor="AWS",
                amount=-120.00,
            )
        ],
        chart_of_accounts=_chart(),
    )

    response = service.classify_batch(request)
    decision = response.results[0]

    assert decision.transaction_type == AccountCategory.EXPENSE
    assert decision.account_code == "6100"
    assert decision.confidence > 0.5
    assert decision.matched_signals
    assert "account_code" in decision.integration_payload


def test_feedback_rule_overrides_base_scoring():
    service = AccountingClassifierService()
    service._feedback_rules = []
    service.register_feedback_rule(
        FeedbackRuleRequest(pattern="contoso", account_code="4000")
    )
    request = ClassificationRequest(
        transactions=[
            TransactionInput(
                transaction_id="t-2",
                description="Payment from Contoso contract",
                vendor="Contoso LLC",
                amount=2500.00,
            )
        ],
        chart_of_accounts=_chart(),
    )

    response = service.classify_batch(request)
    decision = response.results[0]

    assert decision.account_code == "4000"
    assert decision.confidence == 0.98
    assert "Mapping rule matched" in decision.matched_signals[0]
