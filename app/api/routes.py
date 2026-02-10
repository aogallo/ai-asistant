from fastapi import APIRouter, Depends

from app.schemas.ai import SummarizeRequest, SummarizeResponse
from app.services.llm_service import LLMService
from app.services.prompt_service import build_summary_prompt

router = APIRouter()


def get_llm_service() -> LLMService:
    return LLMService()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    request: SummarizeRequest,
    llm: LLMService = Depends(get_llm_service),
) -> SummarizeResponse:
    prompt = build_summary_prompt(request.text)
    summary = await llm.summarize(prompt)

    return SummarizeResponse(text=summary)
