from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


# psycopg/libpq-style query keys that SQLAlchemy may forward to asyncpg.connect().
# asyncpg accepts ssl=..., but not sslmode=... or certificate file options.
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
_TRUE_VALUES = {"true", "1", "require"}
_TLS_SSLMODES = {"require", "verify-ca", "verify-full"}


def asyncpg_engine_options(raw_url: str) -> tuple[str, dict]:
    """Return a sanitized asyncpg URL and SQLAlchemy engine kwargs."""
    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, {}

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query = {key.lower(): value for key, value in query_pairs}

    connect_args: dict = {}
    sslmode = query.get("sslmode", "").lower()
    ssl = query.get("ssl", "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")
    is_pooler = (
        query.get("pgbouncer", "").lower() in _TRUE_VALUES
        or host.endswith(".pooler.supabase.com")
        or parsed.port == 6543
    )

    if sslmode in _TLS_SSLMODES or ssl in _TRUE_VALUES or is_supabase:
        connect_args["ssl"] = True

    kept_pairs = [(key, value) for key, value in query_pairs if key.lower() not in _ASYNCPG_URL_QUERY_DROP]

    if is_pooler:
        connect_args["statement_cache_size"] = 0
        if not any(key.lower() == "prepared_statement_cache_size" for key, _ in kept_pairs):
            kept_pairs.append(("prepared_statement_cache_size", "0"))

    sanitized_url = urlunparse(parsed._replace(query=urlencode(kept_pairs)))
    engine_kwargs = {"connect_args": connect_args} if connect_args else {}
    return sanitized_url, engine_kwargs
