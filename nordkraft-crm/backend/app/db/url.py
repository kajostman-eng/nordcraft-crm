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


def make_asyncpg_url_and_kwargs(raw: str) -> tuple[str, dict]:
    """Return an asyncpg-safe SQLAlchemy URL and engine keyword arguments."""
    connect_args: dict = {}
    engine_kwargs: dict = {"echo": False}
    url = raw

    if raw.startswith("postgresql+asyncpg://"):
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        qs = parse_qs(parsed.query, keep_blank_values=True)

        sslmode = (qs.get("sslmode", [None])[0] or "").lower()
        ssl = (qs.get("ssl", [None])[0] or "").lower()
        is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

        # Ensure TLS when connecting to Supabase or when sslmode/ssl requested.
        if sslmode in {"require", "verify-ca", "verify-full"} or ssl in {"true", "1", "require"} or is_supabase:
            connect_args["ssl"] = "require"

        pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
        is_pooler = pgbouncer in {"true", "1"} or host.endswith(".pooler.supabase.com") or parsed.port == 6543

        kept_pairs = []
        for key, values in qs.items():
            lower_key = key.lower()
            if lower_key in _ASYNCPG_URL_QUERY_DROP:
                continue
            if is_pooler and lower_key == "prepared_statement_cache_size":
                continue
            kept_pairs.extend((key, value) for value in values)

        if is_pooler:
            kept_pairs.append(("prepared_statement_cache_size", "0"))

        new_query = urlencode(kept_pairs, doseq=True) if kept_pairs else ""
        url = urlunparse(parsed._replace(query=new_query))

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

    return url, engine_kwargs
