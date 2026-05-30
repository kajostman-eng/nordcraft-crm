from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.db.url import make_asyncpg_url_and_kwargs


def _engine():
    url, engine_kwargs = make_asyncpg_url_and_kwargs(settings.DATABASE_URL)
    return create_async_engine(url, **engine_kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
