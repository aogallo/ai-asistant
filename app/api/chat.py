from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.services.ll_stream_service import LLMStreamService

router = APIRouter()


@router.post("/chat/stream")
async def stream_chat(prompt: str, service: LLMStreamService = Depends()):
    async def event_generator():
        async for chunk in service.stream_completion(prompt):
            yield chunk

    return StreamingResponse(content=event_generator(), media_type="text/plain")
