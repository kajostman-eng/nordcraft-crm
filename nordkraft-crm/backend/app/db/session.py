from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.db.url import normalize_asyncpg_url


def _engine():
    db_url = normalize_asyncpg_url(settings.DATABASE_URL)
    engine_kwargs: dict = {"echo": False}
    if db_url.connect_args:
        engine_kwargs["connect_args"] = db_url.connect_args
    if db_url.uses_external_pooler:
        engine_kwargs["poolclass"] = NullPool

    return create_async_engine(db_url.url, **engine_kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
