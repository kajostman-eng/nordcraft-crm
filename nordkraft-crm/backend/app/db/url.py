from __future__ import annotations

import ssl
import uuid
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


# libpq-style query keys that SQLAlchemy may forward to asyncpg.connect().
# asyncpg accepts TLS configuration via the "ssl" connect argument instead.
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


def _tls_context_for_sslmode(sslmode: str) -> ssl.SSLContext | bool | None:
    if sslmode in {"", "allow", "prefer"}:
        return None
    if sslmode == "disable":
        return False
    if sslmode == "require":
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    if sslmode == "verify-ca":
        context = ssl.create_default_context()
        context.check_hostname = False
        return context
    if sslmode == "verify-full":
        return ssl.create_default_context()
    return None


def _pooler_prepared_statement_name() -> str:
    return f"__asyncpg_{uuid.uuid4()}__"


def asyncpg_engine_options(raw_url: str, *, echo: bool = False) -> tuple[str, dict]:
    """Return an asyncpg-safe SQLAlchemy URL and engine kwargs."""
    engine_kwargs: dict = {"echo": echo}

    if not raw_url.startswith("postgresql+asyncpg://"):
        return raw_url, engine_kwargs

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    qs = parse_qs(parsed.query)

    sslmode = (qs.get("sslmode", [None])[0] or "").lower()
    ssl_param = (qs.get("ssl", [None])[0] or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")
    is_pooler = (
        (qs.get("pgbouncer", [None])[0] or "").lower() in {"true", "1"}
        or parsed.port == 6543
        or host.endswith(".pooler.supabase.com")
    )

    connect_args: dict = {}

    tls_context = _tls_context_for_sslmode(sslmode)
    if tls_context is not None:
        connect_args["ssl"] = tls_context
    elif ssl_param in {"true", "1", "require"} or is_supabase:
        connect_args["ssl"] = _tls_context_for_sslmode("require")
    elif ssl_param in {"verify-ca", "verify-full"}:
        connect_args["ssl"] = _tls_context_for_sslmode(ssl_param)
    elif ssl_param == "disable":
        connect_args["ssl"] = False

    kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
    if is_pooler:
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_name_func"] = _pooler_prepared_statement_name
        kept["prepared_statement_cache_size"] = ["0"]

    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    pairs = [(k, item) for k, vals in kept.items() for item in vals]
    new_query = urlencode(pairs, doseq=True) if pairs else ""
    url = urlunparse(parsed._replace(query=new_query))
    return url, engine_kwargs
