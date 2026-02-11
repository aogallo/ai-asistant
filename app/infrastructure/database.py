import ssl
from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.core.config import settings


def _prepare_asyncpg_url(url: str) -> tuple[str, dict]:
    """Strip sslmode from URL and return connect_args for asyncpg."""
    parts = urlsplit(url)
    params = parse_qs(parts.query)
    connect_args: dict = {}

    if "sslmode" in params:
        sslmode = params.pop("sslmode")[0]
        if sslmode == "require":
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx

        clean_query = urlencode(params, doseq=True)
        parts = parts._replace(query=clean_query)

    return urlunsplit(parts), connect_args


_db_url = settings.database_url
_engine_kwargs: dict = {"echo": False}

if "sqlite" not in _db_url:
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10

    is_pg = "asyncpg" in _db_url or "postgresql" in _db_url
    if is_pg:
        clean_url, connect_args = _prepare_asyncpg_url(_db_url)
    else:
        clean_url = _db_url
        connect_args = {}

    _engine_kwargs["connect_args"] = connect_args
else:
    clean_url = _db_url

engine = create_async_engine(clean_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
