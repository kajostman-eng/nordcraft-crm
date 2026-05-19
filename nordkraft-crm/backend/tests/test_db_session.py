from app.db.session import _asyncpg_engine_config


def test_pgbouncer_disables_sqlalchemy_prepared_statement_cache():
    url, kwargs = _asyncpg_engine_config(
        "postgresql+asyncpg://user:pass@example.pooler.supabase.com:6543/db?pgbouncer=true&sslmode=require"
    )

    assert "pgbouncer" not in url
    assert "sslmode" not in url
    assert "prepared_statement_cache_size=0" in url
    assert kwargs["connect_args"]["statement_cache_size"] == 0
    assert kwargs["connect_args"]["ssl"] == "require"


def test_verified_sslmode_becomes_ssl_context_and_strips_libpq_query_keys():
    url, kwargs = _asyncpg_engine_config(
        "postgresql+asyncpg://user:pass@db.example.com:5432/app?sslmode=verify-full&application_name=crm"
    )

    assert "sslmode" not in url
    assert "application_name=crm" in url
    assert kwargs["connect_args"]["ssl"].check_hostname is True
