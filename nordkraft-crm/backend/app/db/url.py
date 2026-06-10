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


def async_engine_config(raw_url: str) -> tuple[str, dict]:
    connect_args: dict = {}
    engine_kwargs: dict = {}
    url = raw_url

    if raw_url.startswith("postgresql+asyncpg://"):
        parsed = urlparse(raw_url)
        host = (parsed.hostname or "").lower()
        port = parsed.port
        qs = parse_qs(parsed.query)

        sslmode = (qs.get("sslmode", [None])[0] or "").lower()
        ssl = (qs.get("ssl", [None])[0] or "").lower()
        is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

        # Ensure TLS when connecting to Supabase or when sslmode/ssl requested.
        if sslmode in {"require", "verify-ca", "verify-full"} or ssl in {"true", "1", "require"} or is_supabase:
            connect_args["ssl"] = "require"

        # Supabase's pooler uses PgBouncer. Disable both asyncpg's statement cache
        # and SQLAlchemy's asyncpg prepared-statement cache for pooler safety.
        pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
        uses_pooler = pgbouncer in {"true", "1"} or host.endswith(".pooler.supabase.com") or port == 6543
        if uses_pooler:
            connect_args["statement_cache_size"] = 0

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

        kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
        if uses_pooler and "prepared_statement_cache_size" not in {k.lower() for k in kept}:
            kept["prepared_statement_cache_size"] = ["0"]

        pairs = [(k, item) for k, vals in kept.items() for item in vals]
        new_query = urlencode(pairs, doseq=True) if pairs else ""
        url = urlunparse(parsed._replace(query=new_query))

    return url, engine_kwargs
