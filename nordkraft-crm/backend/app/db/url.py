from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


# psycopg / libpq-style query keys that SQLAlchemy may forward to asyncpg.connect(),
# which accepts ssl=... as a connect argument instead of sslmode=... URL options.
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
    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, {}

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    qs = parse_qs(parsed.query, keep_blank_values=True)
    normalized_qs = {key.lower(): values for key, values in qs.items()}
    connect_args: dict = {}

    sslmode = (normalized_qs.get("sslmode", [None])[0] or "").lower()
    ssl = (normalized_qs.get("ssl", [None])[0] or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")
    if sslmode in {"require", "verify-ca", "verify-full"} or ssl in {"true", "1", "require"} or is_supabase:
        connect_args["ssl"] = True

    pgbouncer = (normalized_qs.get("pgbouncer", [None])[0] or "").lower()
    uses_pooler = pgbouncer in {"true", "1"} or host.endswith(".pooler.supabase.com") or parsed.port == 6543
    if uses_pooler:
        connect_args["statement_cache_size"] = 0

    kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
    if uses_pooler and "prepared_statement_cache_size" not in {k.lower() for k in kept}:
        kept["prepared_statement_cache_size"] = ["0"]

    pairs = [(key, item) for key, values in kept.items() for item in values]
    query = urlencode(pairs, doseq=True) if pairs else ""
    return urlunparse(parsed._replace(query=query)), connect_args
