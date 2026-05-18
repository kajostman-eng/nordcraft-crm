import ssl as ssl_module
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# psycopg / libpq-style query keys that SQLAlchemy may forward to asyncpg.connect(),
# which only accepts ssl=... as a top-level keyword.
_ASYNCPG_URL_QUERY_DROP = frozenset(
    {
        "sslmode",
        "ssl",
        "sslrootcert",
        "sslcert",
        "sslkey",
        "sslpassword",
        "sslcrl",
        "channel_binding",
        "pgbouncer",
    }
)

_ASYNCPG_TLS_MODES = {"allow", "prefer", "require", "verify-ca", "verify-full"}
_ASYNCPG_CERT_QUERY_KEYS = {"sslrootcert", "sslcert", "sslkey", "sslpassword", "sslcrl"}


def _query_value(qs: dict[str, list[str]], key: str) -> str | None:
    value = qs.get(key, [None])[0]
    return value or None


def _certificate_option_present(qs: dict[str, list[str]]) -> bool:
    return any(_query_value(qs, key) for key in _ASYNCPG_CERT_QUERY_KEYS)


def _ssl_context_from_query(sslmode: str, qs: dict[str, list[str]]) -> ssl_module.SSLContext:
    sslrootcert = _query_value(qs, "sslrootcert")
    sslcert = _query_value(qs, "sslcert")
    sslkey = _query_value(qs, "sslkey")
    sslpassword = _query_value(qs, "sslpassword")
    sslcrl = _query_value(qs, "sslcrl")

    if sslmode in {"verify-ca", "verify-full"} or sslrootcert:
        context = ssl_module.create_default_context(cafile=sslrootcert)
        context.check_hostname = sslmode == "verify-full"
        context.verify_mode = ssl_module.CERT_REQUIRED
    else:
        context = ssl_module.SSLContext(ssl_module.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl_module.CERT_NONE

    if sslcrl:
        context.load_verify_locations(cafile=sslcrl)
        context.verify_flags |= ssl_module.VERIFY_CRL_CHECK_CHAIN

    if sslcert:
        context.load_cert_chain(sslcert, keyfile=sslkey, password=sslpassword)

    return context


def _asyncpg_ssl_arg(qs: dict[str, list[str]], host: str):
    sslmode = (_query_value(qs, "sslmode") or "").lower()
    ssl = (_query_value(qs, "ssl") or "").lower()
    is_supabase = host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")

    if sslmode == "disable" or ssl in {"false", "0", "disable"}:
        return False

    requested_mode = sslmode if sslmode in _ASYNCPG_TLS_MODES else None
    if requested_mode is None:
        if ssl in _ASYNCPG_TLS_MODES:
            requested_mode = ssl
        elif ssl in {"true", "1"}:
            requested_mode = "require"

    if requested_mode in {"require", "verify-ca", "verify-full"} and _certificate_option_present(qs):
        return _ssl_context_from_query(requested_mode, qs)

    if requested_mode:
        return requested_mode

    if is_supabase:
        return "require"

    return None


def _asyncpg_engine_options(raw: str) -> tuple[str, dict]:
    connect_args: dict = {}
    engine_kwargs: dict = {"echo": False}
    url = raw

    if raw.startswith("postgresql+asyncpg://"):
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        qs = parse_qs(parsed.query, keep_blank_values=True)

        ssl_arg = _asyncpg_ssl_arg(qs, host)
        if ssl_arg is not None:
            connect_args["ssl"] = ssl_arg

        # If using pgBouncer/transaction pooler, asyncpg statement cache must be disabled.
        pgbouncer = (_query_value(qs, "pgbouncer") or "").lower()
        if pgbouncer in {"true", "1"}:
            connect_args["statement_cache_size"] = 0

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

        # Drop keys asyncpg rejects; TLS is handled via connect_args above.
        kept = {k: v for k, v in qs.items() if k.lower() not in _ASYNCPG_URL_QUERY_DROP}
        pairs = [(k, item) for k, vals in kept.items() for item in vals]
        new_query = urlencode(pairs, doseq=True) if pairs else ""
        url = urlunparse(parsed._replace(query=new_query))

    return url, engine_kwargs


def _engine():
    raw = settings.DATABASE_URL
    url, engine_kwargs = _asyncpg_engine_options(raw)
    return create_async_engine(url, **engine_kwargs)


engine = _engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
