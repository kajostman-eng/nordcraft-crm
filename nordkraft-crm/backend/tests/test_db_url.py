import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import async_engine_config


class AsyncEngineConfigTest(unittest.TestCase):
    def test_strips_libpq_tls_options_and_sets_asyncpg_ssl(self):
        url, engine_kwargs = async_engine_config(
            "postgresql+asyncpg://user:pass@db.example.supabase.co:5432/app"
            "?sslmode=verify-full&sslrootcert=/tmp/root.crt&application_name=crm"
        )

        query = parse_qs(urlparse(url).query)
        self.assertNotIn("sslmode", query)
        self.assertNotIn("sslrootcert", query)
        self.assertEqual(query["application_name"], ["crm"])
        self.assertEqual(engine_kwargs["connect_args"]["ssl"], "require")

    def test_supabase_pooler_disables_asyncpg_and_sqlalchemy_statement_caches(self):
        url, engine_kwargs = async_engine_config(
            "postgresql+asyncpg://user:pass@aws-0-eu-central-1.pooler.supabase.com:6543/app"
            "?sslmode=require"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(engine_kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertEqual(engine_kwargs["connect_args"]["ssl"], "require")

    def test_explicit_pgbouncer_flag_disables_statement_caches(self):
        url, engine_kwargs = async_engine_config(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app?pgbouncer=true"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(engine_kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertNotIn("pgbouncer", query)


if __name__ == "__main__":
    unittest.main()
