from fastapi import FastAPI

from app.api.routes import router
from app.api.chat import router as chat_router

app = FastAPI(title="AI FastAPI Template")

app.include_router(router)
app.include_router(chat_router)
