from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.db.url import async_engine_config


def _engine():
    url, engine_kwargs = async_engine_config(settings.DATABASE_URL)
    engine_kwargs["echo"] = False
    return create_async_engine(url, **engine_kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
