from __future__ import annotations

import ssl
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


# psycopg / libpq-style query keys that SQLAlchemy may forward to
# asyncpg.connect(), which does not accept them directly.
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


def build_asyncpg_engine_config(raw_url: str) -> tuple[str, dict]:
    """Translate Postgres URL options into SQLAlchemy asyncpg engine settings."""
    engine_kwargs: dict = {"echo": False}
    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, engine_kwargs

    parsed = urlparse(raw_url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    host = (parsed.hostname or "").lower()

    connect_args: dict = {}
    ssl_arg = _ssl_connect_arg(query, _is_supabase_host(host))
    if ssl_arg is not None:
        connect_args["ssl"] = ssl_arg

    pooled = _uses_transaction_pooler(parsed, query)
    if pooled:
        connect_args["statement_cache_size"] = 0

    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    kept = {
        key: values
        for key, values in query.items()
        if key.lower() not in _ASYNCPG_URL_QUERY_DROP
        and not (pooled and key.lower() == "prepared_statement_cache_size")
    }
    if pooled:
        # SQLAlchemy's asyncpg dialect has its own prepared statement cache.
        # It must be disabled separately from asyncpg's statement_cache_size
        # when a PgBouncer/Supabase transaction pooler can swap server sessions.
        kept["prepared_statement_cache_size"] = ["0"]

    pairs = [(key, item) for key, values in kept.items() for item in values]
    normalized_url = urlunparse(
        parsed._replace(query=urlencode(pairs, doseq=True) if pairs else "")
    )
    return normalized_url, engine_kwargs


def _query_value(query: dict[str, list[str]], name: str) -> str:
    name = name.lower()
    for key, values in query.items():
        if key.lower() == name:
            return (values[0] if values else "") or ""
    return ""


def _is_supabase_host(host: str) -> bool:
    return host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")


def _uses_transaction_pooler(parsed, query: dict[str, list[str]]) -> bool:
    host = (parsed.hostname or "").lower()
    pgbouncer = _query_value(query, "pgbouncer").lower()
    return (
        pgbouncer in {"true", "1", "yes"}
        or host.endswith(".pooler.supabase.com")
        or (_is_supabase_host(host) and parsed.port == 6543)
    )


def _ssl_connect_arg(query: dict[str, list[str]], is_supabase: bool):
    sslmode = _query_value(query, "sslmode").lower()
    ssl_query = _query_value(query, "ssl").lower()

    if sslmode == "disable" or ssl_query in {"false", "0", "disable"}:
        return None

    if sslmode in {"require", "verify-ca", "verify-full"}:
        return _ssl_context(query, sslmode)

    if ssl_query in {"true", "1", "require", "verify-ca", "verify-full"}:
        mode = ssl_query if ssl_query in {"verify-ca", "verify-full"} else "require"
        return _ssl_context(query, mode)

    if is_supabase:
        return _ssl_context(query, "verify-full")

    return None


def _ssl_context(query: dict[str, list[str]], sslmode: str) -> ssl.SSLContext:
    root_cert = _query_value(query, "sslrootcert") or None
    if sslmode == "require":
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    else:
        context = ssl.create_default_context(cafile=root_cert)
        context.check_hostname = sslmode == "verify-full"

    cert_file = _query_value(query, "sslcert") or None
    if cert_file:
        context.load_cert_chain(
            certfile=cert_file,
            keyfile=_query_value(query, "sslkey") or None,
        )
    return context
