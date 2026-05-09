from urllib.parse import urlparse, parse_qs

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings


def _engine():
    url = settings.DATABASE_URL
    connect_args: dict = {}
    engine_kwargs: dict = {"echo": False}

    if url.startswith("postgresql+asyncpg://"):
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        qs = parse_qs(parsed.query)

        sslmode = (qs.get("sslmode", [None])[0] or "").lower()
        ssl = (qs.get("ssl", [None])[0] or "").lower()
        is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

        # Ensure TLS when connecting to Supabase or when sslmode/ssl requested.
        if sslmode == "require" or ssl in {"true", "1", "require"} or is_supabase:
            connect_args["ssl"] = "require"

        # If using pgBouncer/transaction pooler, asyncpg statement cache must be disabled.
        pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
        if pgbouncer in {"true", "1"}:
            connect_args["statement_cache_size"] = 0

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
