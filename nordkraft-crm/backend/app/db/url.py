from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from uuid import uuid4


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


@dataclass(frozen=True)
class DatabaseUrlConfig:
    url: str
    connect_args: dict[str, Any]
    uses_external_pooler: bool = False


def _first_query_value(query_pairs: list[tuple[str, str]], key: str) -> str:
    key = key.lower()
    for pair_key, value in query_pairs:
        if pair_key.lower() == key:
            return value.lower()
    return ""


def _port(parsed_url) -> int | None:
    try:
        return parsed_url.port
    except ValueError:
        return None


def normalize_asyncpg_url(raw_url: str) -> DatabaseUrlConfig:
    if not raw_url.startswith("postgresql+asyncpg://"):
        return DatabaseUrlConfig(raw_url, {})

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)

    sslmode = _first_query_value(query_pairs, "sslmode")
    ssl = _first_query_value(query_pairs, "ssl")
    pgbouncer = _first_query_value(query_pairs, "pgbouncer")

    is_supabase_pooler = host.endswith(".pooler.supabase.com")
    is_supabase = host.endswith(".supabase.co") or is_supabase_pooler
    uses_external_pooler = (
        pgbouncer in {"true", "1"}
        or is_supabase_pooler
        or _port(parsed) == 6543
    )

    connect_args: dict[str, Any] = {}
    if (
        sslmode in {"require", "verify-ca", "verify-full"}
        or ssl in {"true", "1", "require"}
        or is_supabase
    ):
        connect_args["ssl"] = True

    kept_pairs = [
        (key, value)
        for key, value in query_pairs
        if key.lower() not in _ASYNCPG_URL_QUERY_DROP
    ]

    if uses_external_pooler:
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_name_func"] = (
            lambda: f"__asyncpg_{uuid4()}__"
        )
        kept_pairs = [
            (key, value)
            for key, value in kept_pairs
            if key.lower() != "prepared_statement_cache_size"
        ]
        kept_pairs.append(("prepared_statement_cache_size", "0"))

    query = urlencode(kept_pairs, doseq=True) if kept_pairs else ""
    return DatabaseUrlConfig(
        urlunparse(parsed._replace(query=query)),
        connect_args,
        uses_external_pooler,
    )
