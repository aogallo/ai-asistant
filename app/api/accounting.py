from fastapi import APIRouter, Depends

from app.schemas.accounting import (
    ClassificationRequest,
    ClassificationResponse,
    FeedbackResponse,
    FeedbackRuleRequest,
)
from app.services.accounting_classifier_service import (
    AccountingClassifierService,
)

router = APIRouter(prefix="/accounting", tags=["accounting"])


def get_classifier_service() -> AccountingClassifierService:
    return AccountingClassifierService()


@router.post("/classify", response_model=ClassificationResponse)
async def classify_transactions(
    request: ClassificationRequest,
    service: AccountingClassifierService = Depends(get_classifier_service),
) -> ClassificationResponse:
    return service.classify_batch(request)


@router.post("/feedback", response_model=FeedbackResponse)
async def add_feedback_rule(
    request: FeedbackRuleRequest,
    service: AccountingClassifierService = Depends(get_classifier_service),
) -> FeedbackResponse:
    total_rules = service.register_feedback_rule(request)
    return FeedbackResponse(status="ok", total_rules=total_rules)
