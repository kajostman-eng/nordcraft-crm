from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


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
_PREPARED_STATEMENT_CACHE_KEY = "prepared_statement_cache_size"


def _query_value(qs: dict, key: str) -> str:
    key = key.lower()
    for existing_key, values in qs.items():
        if existing_key.lower() == key:
            return (values[0] if values else "") or ""
    return ""


def _uses_transaction_pooler(parsed, qs: dict) -> bool:
    host = (parsed.hostname or "").lower()
    pgbouncer = _query_value(qs, "pgbouncer").lower()

    if pgbouncer in {"true", "1", "yes"}:
        return True

    # Supabase pooler hosts and port 6543 use PgBouncer transaction pooling.
    if host.endswith(".pooler.supabase.com"):
        return True

    return parsed.port == 6543 and host.endswith(".supabase.co")


def asyncpg_engine_config(raw: str) -> tuple[str, dict]:
    connect_args: dict = {}
    engine_kwargs: dict = {"echo": False}
    url = raw

    if raw.startswith("postgresql+asyncpg://"):
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        qs = parse_qs(parsed.query)

        sslmode = _query_value(qs, "sslmode").lower()
        ssl = _query_value(qs, "ssl").lower()
        is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

        # Ensure TLS when connecting to Supabase or when sslmode/ssl requested.
        if sslmode == "require" or ssl in {"true", "1", "require"} or is_supabase:
            connect_args["ssl"] = "require"

        # If using pgBouncer/transaction pooler, asyncpg statement cache must be disabled.
        uses_transaction_pooler = _uses_transaction_pooler(parsed, qs)
        if uses_transaction_pooler:
            connect_args["statement_cache_size"] = 0

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

        # Drop keys asyncpg rejects; TLS is handled via connect_args above.
        kept = {
            k: v
            for k, v in qs.items()
            if k.lower() not in _ASYNCPG_URL_QUERY_DROP
            and k.lower() != _PREPARED_STATEMENT_CACHE_KEY
        }
        if uses_transaction_pooler:
            kept[_PREPARED_STATEMENT_CACHE_KEY] = ["0"]
        pairs = [(k, item) for k, vals in kept.items() for item in vals]
        new_query = urlencode(pairs, doseq=True) if pairs else ""
        url = urlunparse(parsed._replace(query=new_query))

    return url, engine_kwargs
