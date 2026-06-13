from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


# psycopg/libpq-style query keys that asyncpg rejects when SQLAlchemy forwards
# them into asyncpg.connect().
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


def normalize_asyncpg_url(raw_url: str) -> tuple[str, dict]:
    """Return an asyncpg-safe SQLAlchemy URL and connect_args."""
    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, {}

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    qs = parse_qs(parsed.query)
    connect_args: dict = {}

    sslmode = (qs.get("sslmode", [None])[0] or "").lower()
    ssl = (qs.get("ssl", [None])[0] or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

    # Supabase and libpq sslmode=require URLs need TLS, but asyncpg expects the
    # setting in connect_args rather than the URL query string.
    if sslmode in {"require", "verify-ca", "verify-full"} or ssl in {"true", "1", "require"} or is_supabase:
        connect_args["ssl"] = "require"

    pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
    uses_transaction_pooler = (
        pgbouncer in {"true", "1"}
        or host.endswith(".pooler.supabase.com")
        or parsed.port == 6543
    )
    if uses_transaction_pooler:
        connect_args["statement_cache_size"] = 0

    kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
    if uses_transaction_pooler:
        # SQLAlchemy's asyncpg dialect has its own prepared statement cache in
        # addition to asyncpg's driver cache; both must be disabled for PgBouncer.
        kept["prepared_statement_cache_size"] = ["0"]

    pairs = [(k, item) for k, vals in kept.items() for item in vals]
    normalized_query = urlencode(pairs, doseq=True) if pairs else ""
    return urlunparse(parsed._replace(query=normalized_query)), connect_args
