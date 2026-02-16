from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.accounting import router as accounting_router
from app.api.agent import router as agent_router
from app.api.chat import router as chat_router
from app.api.invoices import router as invoice_router
from app.api.routes import router
from app.infrastructure.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


app = FastAPI(title="AI FastAPI Template", lifespan=lifespan)

app.include_router(router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(invoice_router)
app.include_router(accounting_router)
