from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


# libpq-style query keys that asyncpg does not accept when SQLAlchemy forwards
# URL parameters to the driver. TLS is translated into connect_args below.
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


def asyncpg_engine_config(raw_url: str) -> tuple[str, dict]:
    """Return a SQLAlchemy asyncpg URL plus kwargs safe for runtime and Alembic."""
    engine_kwargs: dict = {"echo": False}
    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, engine_kwargs

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    port = parsed.port
    qs = parse_qs(parsed.query)

    sslmode = (qs.get("sslmode", [None])[0] or "").lower()
    ssl = (qs.get("ssl", [None])[0] or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

    connect_args: dict = {}
    if sslmode in {"require", "verify-ca", "verify-full"} or ssl in {"true", "1", "require"} or is_supabase:
        connect_args["ssl"] = "require"

    pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
    uses_pooler = pgbouncer in {"true", "1"} or host.endswith(".pooler.supabase.com") or port == 6543
    if uses_pooler:
        connect_args["statement_cache_size"] = 0

    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
    if uses_pooler:
        kept["prepared_statement_cache_size"] = ["0"]

    pairs = [(key, item) for key, vals in kept.items() for item in vals]
    new_query = urlencode(pairs, doseq=True) if pairs else ""
    return urlunparse(parsed._replace(query=new_query)), engine_kwargs
