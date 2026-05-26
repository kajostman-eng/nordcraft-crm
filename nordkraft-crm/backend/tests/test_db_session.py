import ssl
import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import normalize_asyncpg_url


class AsyncpgUrlNormalizationTests(unittest.TestCase):
    def test_verified_sslmode_is_translated_to_ssl_context(self):
        url, engine_kwargs = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?sslmode=verify-full&application_name=crm"
        )

        query = parse_qs(urlparse(url).query)
        self.assertNotIn("sslmode", query)
        self.assertEqual(query["application_name"], ["crm"])

        ssl_arg = engine_kwargs["connect_args"]["ssl"]
        self.assertIsInstance(ssl_arg, ssl.SSLContext)
        self.assertTrue(ssl_arg.check_hostname)
        self.assertEqual(ssl_arg.verify_mode, ssl.CERT_REQUIRED)

    def test_pgbouncer_query_disables_sqlalchemy_and_asyncpg_statement_caches(self):
        url, engine_kwargs = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?pgbouncer=true&sslmode=require"
        )

        query = parse_qs(urlparse(url).query)
        self.assertNotIn("pgbouncer", query)
        self.assertNotIn("sslmode", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(engine_kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(engine_kwargs["connect_args"]["statement_cache_size"], 0)

    def test_supabase_pooler_port_disables_statement_caches(self):
        url, engine_kwargs = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?sslmode=require"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(engine_kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertEqual(engine_kwargs["connect_args"]["ssl"], "require")


if __name__ == "__main__":
    unittest.main()
