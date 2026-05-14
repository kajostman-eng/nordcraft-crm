from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from uuid import uuid4

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

_ASYNCPG_SSL_OPTIONS = frozenset(
    {
        "disable",
        "allow",
        "prefer",
        "require",
        "verify-ca",
        "verify-full",
    }
)

_PGBOUNCER_URL_QUERY_DROP = frozenset(
    {
        "prepared_statement_cache_size",
        "statement_cache_size",
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
        is_supabase = host.endswith(".supabase.co") or host.endswith(
            ".pooler.supabase.com"
        )

        if sslmode in _ASYNCPG_SSL_OPTIONS:
            connect_args["ssl"] = sslmode
        elif ssl in _ASYNCPG_SSL_OPTIONS:
            connect_args["ssl"] = ssl
        elif ssl in {"true", "1"} or is_supabase:
            connect_args["ssl"] = "require"
        elif ssl in {"false", "0"}:
            connect_args["ssl"] = "disable"

        pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
        uses_pgbouncer = pgbouncer in {"true", "1"} or host.endswith(
            ".pooler.supabase.com"
        )

        if uses_pgbouncer:
            # SQLAlchemy's asyncpg dialect has its own prepared-statement cache
            # in addition to asyncpg's driver cache. Both must be disabled for
            # PgBouncer transaction/statement pooling, and names must not collide
            # with statements left behind on pooled server connections.
            connect_args["statement_cache_size"] = 0
            connect_args["prepared_statement_cache_size"] = 0
            connect_args["prepared_statement_name_func"] = (
                lambda: f"__asyncpg_{uuid4()}__"
            )

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

        # Drop keys asyncpg rejects; TLS is handled via connect_args above.
        drop_keys = set(_ASYNCPG_URL_QUERY_DROP)
        if uses_pgbouncer:
            drop_keys.update(_PGBOUNCER_URL_QUERY_DROP)

        kept = {k: v for k, v in qs.items() if k.lower() not in drop_keys}
        pairs = [(k, item) for k, vals in kept.items() for item in vals]
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
