from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.agents.agent_loop import ClaudeAgentLoop


router = APIRouter()


@router.post("/agent/stream", response_model=None)
async def stream_agent(prompt: str, agent: ClaudeAgentLoop = Depends()):
    async def generator():
        async for chunk in agent.run(prompt):
            yield chunk

    return StreamingResponse(generator(), media_type="text/plain")
