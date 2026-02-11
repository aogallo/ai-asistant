from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.services.ll_stream_service import LLMStreamService

router = APIRouter()


@router.post("/chat/stream", response_model=None)
async def stream_chat(prompt: str, service: LLMStreamService = Depends()):
    async def event_generator():
        async for chunk in service.stream_completation(prompt):
            yield chunk

    return StreamingResponse(content=event_generator(), media_type="text/plain")
