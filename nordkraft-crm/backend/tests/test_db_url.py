import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import asyncpg_engine_config


def query_params(url: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(url).query)


class AsyncpgEngineConfigTests(unittest.TestCase):
    def test_supabase_pooler_disables_prepared_statement_cache_without_flag(self):
        url, kwargs = asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?sslmode=require"
        )

        query = query_params(url)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertNotIn("sslmode", query)
        connect_args = dict(kwargs["connect_args"])
        self.assertTrue(callable(connect_args.pop("prepared_statement_name_func")))
        self.assertEqual(
            connect_args,
            {"ssl": "require", "statement_cache_size": 0},
        )

    def test_explicit_pgbouncer_flag_disables_prepared_statement_cache(self):
        url, kwargs = asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app"
            "?pgbouncer=true&ssl=true&application_name=crm"
        )

        query = query_params(url)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(query["application_name"], ["crm"])
        self.assertNotIn("pgbouncer", query)
        self.assertNotIn("ssl", query)
        connect_args = dict(kwargs["connect_args"])
        self.assertTrue(callable(connect_args.pop("prepared_statement_name_func")))
        self.assertEqual(
            connect_args,
            {"ssl": "require", "statement_cache_size": 0},
        )

    def test_supabase_direct_connection_requires_ssl_without_pooler_cache_change(self):
        url, kwargs = asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@db.project.supabase.co:5432/postgres"
        )

        self.assertEqual(query_params(url), {})
        self.assertEqual(kwargs["connect_args"], {"ssl": "require"})

    def test_non_asyncpg_url_is_unchanged(self):
        raw = "sqlite+aiosqlite:///tmp/test.db"

        url, kwargs = asyncpg_engine_config(raw)

        self.assertEqual(url, raw)
        self.assertEqual(kwargs, {"echo": False})


if __name__ == "__main__":
    unittest.main()
