from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from uuid import uuid4


# psycopg / libpq-style query keys that SQLAlchemy may forward to
# asyncpg.connect(), which accepts ssl=... but not sslmode=...
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


def _prepared_statement_name() -> str:
    return f"__asyncpg_{uuid4()}__"


def asyncpg_engine_config(raw_url: str) -> tuple[str, dict]:
    """Return a SQLAlchemy asyncpg URL plus engine kwargs safe for managed PG."""
    engine_kwargs: dict = {"echo": False}

    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, engine_kwargs

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    port = parsed.port
    qs = parse_qs(parsed.query)
    connect_args: dict = {}

    sslmode = (qs.get("sslmode", [None])[0] or "").lower()
    ssl = (qs.get("ssl", [None])[0] or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

    if sslmode == "require" or ssl in {"true", "1", "require"} or is_supabase:
        connect_args["ssl"] = "require"

    pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
    uses_pooler = pgbouncer in {"true", "1"} or host.endswith(".pooler.supabase.com") or port == 6543

    kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
    if uses_pooler:
        # SQLAlchemy's asyncpg dialect uses this URL option for its prepared
        # statement cache; transaction poolers reject/reuse those statements.
        kept["prepared_statement_cache_size"] = ["0"]
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_name_func"] = _prepared_statement_name

    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    pairs = [(k, item) for k, vals in kept.items() for item in vals]
    new_query = urlencode(pairs, doseq=True) if pairs else ""
    return urlunparse(parsed._replace(query=new_query)), engine_kwargs
