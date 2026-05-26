import ssl
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


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


def _first_query_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key.lower())
    return values[0] if values else ""


def _ssl_context_for_verified_mode(
    sslmode: str, query: dict[str, list[str]]
) -> ssl.SSLContext:
    root_cert = _first_query_value(query, "sslrootcert")
    cert_file = _first_query_value(query, "sslcert")
    key_file = _first_query_value(query, "sslkey")

    context = ssl.create_default_context(cafile=root_cert or None)
    context.check_hostname = sslmode == "verify-full"
    context.verify_mode = ssl.CERT_REQUIRED

    if cert_file:
        context.load_cert_chain(certfile=cert_file, keyfile=key_file or None)

    return context


def _asyncpg_ssl_arg(
    query: dict[str, list[str]], is_supabase: bool
) -> str | ssl.SSLContext | None:
    sslmode = _first_query_value(query, "sslmode").lower()
    ssl_value = _first_query_value(query, "ssl").lower()

    if sslmode in {"verify-ca", "verify-full"}:
        return _ssl_context_for_verified_mode(sslmode, query)

    if ssl_value in {"verify-ca", "verify-full"}:
        return _ssl_context_for_verified_mode(ssl_value, query)

    if sslmode == "require" or ssl_value in {"true", "1", "require"}:
        return "require"

    if is_supabase and sslmode != "disable" and ssl_value not in {"false", "0", "disable"}:
        return "require"

    return None


def _parsed_port(parsed) -> int | None:
    try:
        return parsed.port
    except ValueError:
        return None


def _uses_transaction_pooler(
    host: str, port: int | None, query: dict[str, list[str]]
) -> bool:
    pgbouncer = _first_query_value(query, "pgbouncer").lower()
    is_supabase_pooler = host.endswith(".pooler.supabase.com") or (
        port == 6543 and (host.endswith(".supabase.com") or host.endswith(".supabase.co"))
    )
    return pgbouncer in {"true", "1"} or is_supabase_pooler


def normalize_asyncpg_url(raw: str) -> tuple[str, dict]:
    engine_kwargs: dict = {"echo": False}

    if not raw.startswith("postgresql+asyncpg://"):
        return raw, engine_kwargs

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query: dict[str, list[str]] = {}
    for key, value in pairs:
        query.setdefault(key.lower(), []).append(value)

    connect_args: dict = {}
    is_supabase = host.endswith(".supabase.co") or host.endswith(".supabase.com")
    ssl_arg = _asyncpg_ssl_arg(query, is_supabase)
    if ssl_arg is not None:
        connect_args["ssl"] = ssl_arg

    disable_statement_cache = _uses_transaction_pooler(host, _parsed_port(parsed), query)
    if disable_statement_cache:
        connect_args["statement_cache_size"] = 0

    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    kept_pairs = [(k, v) for k, v in pairs if k.lower() not in _ASYNCPG_URL_QUERY_DROP]
    if disable_statement_cache and "prepared_statement_cache_size" not in query:
        kept_pairs.append(("prepared_statement_cache_size", "0"))

    new_query = urlencode(kept_pairs, doseq=True) if kept_pairs else ""
    return urlunparse(parsed._replace(query=new_query)), engine_kwargs
