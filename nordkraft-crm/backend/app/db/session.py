from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# psycopg / libpq-style query keys that SQLAlchemy may forward to asyncpg.connect(),
# which only accepts ssl=..., not sslmode=...
_ASYNCPG_URL_QUERY_DROP = frozenset(
    {
        "sslmode",
        "ssl",
        "sslrootcert",
        "sslcert",
        "sslkey",
        "channel_binding",
        "pgbouncer",
    }
)


def _engine():
    raw = settings.DATABASE_URL
    connect_args: dict = {}
    engine_kwargs: dict = {"echo": False}
    url = raw

    if raw.startswith("postgresql+asyncpg://"):
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        qs = parse_qs(parsed.query)

        sslmode = (qs.get("sslmode", [None])[0] or "").lower()
        ssl = (qs.get("ssl", [None])[0] or "").lower()
        is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

        # Ensure TLS when connecting to Supabase or when sslmode/ssl requested.
        if sslmode == "require" or ssl in {"true", "1", "require"} or is_supabase:
            connect_args["ssl"] = "require"

        # If using pgBouncer/transaction pooler, asyncpg statement caches must be disabled.
        pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
        use_pgbouncer = pgbouncer in {"true", "1"}
        if use_pgbouncer:
            connect_args["statement_cache_size"] = 0

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

        # Drop keys asyncpg rejects; TLS is handled via connect_args above.
        pairs = [
            (k, item)
            for k, vals in qs.items()
            if k.lower() not in _ASYNCPG_URL_QUERY_DROP
            and not (use_pgbouncer and k.lower() == "prepared_statement_cache_size")
            for item in vals
        ]
        if use_pgbouncer:
            pairs.append(("prepared_statement_cache_size", "0"))
        new_query = urlencode(pairs, doseq=True) if pairs else ""
        url = urlunparse(parsed._replace(query=new_query))

    return create_async_engine(url, **engine_kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
