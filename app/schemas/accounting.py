from enum import Enum

from pydantic import BaseModel, Field


class AccountCategory(str, Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"


class CashFlowDirection(str, Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


class TransactionInput(BaseModel):
    transaction_id: str
    description: str
    vendor: str | None = None
    amount: float
    direction: CashFlowDirection | None = None
    currency: str | None = None


class AccountDefinition(BaseModel):
    code: str
    name: str
    category: AccountCategory
    keywords: list[str] = Field(default_factory=list)
    vendors: list[str] = Field(default_factory=list)
    is_active: bool = True


class AccountMappingRule(BaseModel):
    pattern: str
    account_code: str
    match_vendor_only: bool = False


class ClassificationRequest(BaseModel):
    transactions: list[TransactionInput]
    chart_of_accounts: list[AccountDefinition]
    mapping_rules: list[AccountMappingRule] = Field(default_factory=list)
    target_system: str = "generic"


class ClassificationDecision(BaseModel):
    transaction_id: str
    transaction_type: AccountCategory
    account_code: str
    account_name: str
    confidence: float
    explanation: str
    matched_signals: list[str]
    integration_payload: dict[str, str | float]


class ClassificationResponse(BaseModel):
    results: list[ClassificationDecision]


class FeedbackRuleRequest(BaseModel):
    pattern: str
    account_code: str
    match_vendor_only: bool = False


class FeedbackResponse(BaseModel):
    status: str
    total_rules: int
