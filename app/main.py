from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="AI FastAPI Template")

app.include_router(router)
