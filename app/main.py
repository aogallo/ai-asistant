from fastapi import FastAPI

from app.api.agent import router as agent_router
from app.api.chat import router as chat_router
from app.api.routes import router

app = FastAPI(title="AI FastAPI Template")

app.include_router(router)
app.include_router(chat_router)
app.include_router(agent_router)
