import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import asyncpg_engine_config


class AsyncpgEngineConfigTest(unittest.TestCase):
    def test_strips_libpq_ssl_keys_and_enables_tls(self):
        url, kwargs = asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app"
            "?sslmode=require&channel_binding=require&application_name=crm"
        )

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        self.assertEqual(query, {"application_name": ["crm"]})
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")

    def test_supabase_pooler_disables_prepared_statement_caches(self):
        url, kwargs = asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/app?sslmode=require"
        )

        query = parse_qs(urlparse(url).query)

        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)


if __name__ == "__main__":
    unittest.main()
