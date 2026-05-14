from unittest import TestCase
from unittest.mock import patch

from app.db import session


class SessionEngineTests(TestCase):
    def build_engine(self, database_url):
        with patch.object(session.settings, "DATABASE_URL", database_url), patch.object(
            session, "create_async_engine"
        ) as create_async_engine:
            create_async_engine.return_value = object()
            session._engine()
            return create_async_engine.call_args

    def test_pgbouncer_url_disables_asyncpg_and_sqlalchemy_statement_caches(self):
        call_args = self.build_engine(
            "postgresql+asyncpg://user:pass@db.example.com:6543/app"
            "?sslmode=require&pgbouncer=true&statement_cache_size=100"
            "&prepared_statement_cache_size=100&application_name=crm"
        )

        url, = call_args.args
        kwargs = call_args.kwargs

        self.assertEqual(
            url,
            "postgresql+asyncpg://user:pass@db.example.com:6543/app"
            "?application_name=crm",
        )
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertEqual(kwargs["connect_args"]["prepared_statement_cache_size"], 0)
        name_func = kwargs["connect_args"]["prepared_statement_name_func"]
        self.assertRegex(name_func(), r"^__asyncpg_[0-9a-f-]{36}__$")

    def test_supabase_pooler_host_uses_pgbouncer_safe_defaults(self):
        call_args = self.build_engine(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
        )

        url, = call_args.args
        kwargs = call_args.kwargs

        self.assertEqual(
            url,
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres",
        )
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertEqual(kwargs["connect_args"]["prepared_statement_cache_size"], 0)

    def test_non_pgbouncer_url_preserves_sqlalchemy_prepared_cache_setting(self):
        call_args = self.build_engine(
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?prepared_statement_cache_size=250"
        )

        url, = call_args.args
        kwargs = call_args.kwargs

        self.assertEqual(
            url,
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?prepared_statement_cache_size=250",
        )
        self.assertEqual(kwargs, {"echo": False})

    def test_strict_sslmode_is_preserved_as_asyncpg_ssl_argument(self):
        call_args = self.build_engine(
            "postgresql+asyncpg://user:pass@secure.example.com/app"
            "?sslmode=verify-full"
        )

        url, = call_args.args
        kwargs = call_args.kwargs

        self.assertEqual(url, "postgresql+asyncpg://user:pass@secure.example.com/app")
        self.assertEqual(kwargs["connect_args"]["ssl"], "verify-full")
