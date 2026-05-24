import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from app.db import session


class AsyncpgEngineConfigurationTests(unittest.TestCase):
    def _engine_call(self, database_url: str):
        sentinel = object()
        with (
            patch.object(session.settings, "DATABASE_URL", database_url),
            patch.object(session, "create_async_engine", return_value=sentinel) as create_engine,
        ):
            self.assertIs(session._engine(), sentinel)

        args, kwargs = create_engine.call_args
        return args[0], kwargs

    def test_supabase_transaction_pooler_disables_sqlalchemy_prepared_cache(self):
        url, kwargs = self._engine_call(
            "postgresql+asyncpg://user:pass@db.example.supabase.co:6543/postgres"
            "?sslmode=require&application_name=nordkraft"
        )

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        self.assertNotIn("sslmode", query)
        self.assertEqual(query["application_name"], ["nordkraft"])
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(
            kwargs["connect_args"],
            {"ssl": "require", "statement_cache_size": 0},
        )

    def test_explicit_pgbouncer_flag_disables_prepared_cache_and_is_stripped(self):
        url, kwargs = self._engine_call(
            "postgresql+asyncpg://user:pass@postgres.internal:5432/app"
            "?pgbouncer=true&prepared_statement_cache_size=100"
        )

        query = parse_qs(urlparse(url).query)

        self.assertNotIn("pgbouncer", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"], {"statement_cache_size": 0})

    def test_direct_supabase_connection_keeps_prepared_cache_default(self):
        url, kwargs = self._engine_call(
            "postgresql+asyncpg://user:pass@db.example.supabase.co:5432/postgres"
        )

        self.assertNotIn("prepared_statement_cache_size", parse_qs(urlparse(url).query))
        self.assertEqual(kwargs["connect_args"], {"ssl": "require"})


if __name__ == "__main__":
    unittest.main()
