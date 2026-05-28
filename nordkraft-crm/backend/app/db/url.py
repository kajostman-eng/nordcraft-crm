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


def _normalize_asyncpg_scheme(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    return url


def prepare_asyncpg_url(raw_url: str) -> tuple[str, dict]:
    """Return a SQLAlchemy asyncpg URL plus connect args safe for hosted Postgres."""
    url = _normalize_asyncpg_scheme(raw_url)
    connect_args: dict = {}

    if not url.startswith("postgresql+asyncpg://"):
        return url, connect_args

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    qs = parse_qs(parsed.query, keep_blank_values=True)

    sslmode = (qs.get("sslmode", [None])[0] or "").lower()
    ssl = (qs.get("ssl", [None])[0] or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

    # Ensure TLS when connecting to Supabase or when sslmode/ssl requested.
    if (
        sslmode in {"require", "verify-ca", "verify-full"}
        or ssl in {"true", "1", "require"}
        or is_supabase
    ):
        connect_args["ssl"] = True

    pgbouncer = (qs.get("pgbouncer", [None])[0] or "").lower()
    uses_pooler = (
        pgbouncer in {"true", "1"}
        or host.endswith(".pooler.supabase.com")
        or parsed.port == 6543
    )
    if uses_pooler:
        connect_args["statement_cache_size"] = 0

    # Drop keys asyncpg rejects; TLS is handled via connect_args above.
    kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
    has_prepared_cache_size = any(k.lower() == "prepared_statement_cache_size" for k in kept)
    if uses_pooler and not has_prepared_cache_size:
        kept["prepared_statement_cache_size"] = ["0"]

    pairs = [(k, item) for k, vals in kept.items() for item in vals]
    new_query = urlencode(pairs, doseq=True) if pairs else ""
    return urlunparse(parsed._replace(query=new_query)), connect_args
