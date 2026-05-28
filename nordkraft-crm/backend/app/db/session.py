from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.db.url import prepare_asyncpg_url


def _engine():
    url, connect_args = prepare_asyncpg_url(settings.DATABASE_URL)
    engine_kwargs: dict = {"echo": False}
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    return create_async_engine(url, **engine_kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
