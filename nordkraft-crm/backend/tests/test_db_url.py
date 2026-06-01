import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import asyncpg_engine_options


class AsyncpgEngineOptionsTests(unittest.TestCase):
    def test_translates_sslmode_and_strips_asyncpg_unsupported_query_keys(self):
        url, kwargs = asyncpg_engine_options(
            "postgresql+asyncpg://user:pass@db.supabase.co:5432/postgres"
            "?sslmode=require&sslrootcert=/tmp/root.crt&application_name=crm"
        )

        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        self.assertEqual(kwargs["connect_args"]["ssl"], True)
        self.assertNotIn("sslmode", query)
        self.assertNotIn("sslrootcert", query)
        self.assertEqual(query["application_name"], ["crm"])

    def test_disables_prepared_statement_caches_for_pooler_urls(self):
        url, kwargs = asyncpg_engine_options(
            "postgresql+asyncpg://user:pass@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
            "?sslmode=require&pgbouncer=true"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(kwargs["connect_args"]["ssl"], True)
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertNotIn("pgbouncer", query)
        self.assertNotIn("sslmode", query)

    def test_preserves_existing_prepared_statement_cache_size(self):
        url, kwargs = asyncpg_engine_options(
            "postgresql+asyncpg://user:pass@db.example.com:6543/postgres"
            "?prepared_statement_cache_size=0&pgbouncer=true"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)


if __name__ == "__main__":
    unittest.main()
