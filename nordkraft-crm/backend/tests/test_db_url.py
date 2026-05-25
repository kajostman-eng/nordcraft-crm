import ssl
import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import build_asyncpg_engine_config


class AsyncpgUrlConfigTests(unittest.TestCase):
    def test_non_asyncpg_urls_are_left_unchanged(self):
        url = "sqlite+aiosqlite:///tmp/test.db"

        normalized, kwargs = build_asyncpg_engine_config(url)

        self.assertEqual(normalized, url)
        self.assertEqual(kwargs, {"echo": False})

    def test_sslmode_verify_full_becomes_ssl_context(self):
        url = (
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?sslmode=verify-full&channel_binding=require&application_name=crm"
        )

        normalized, kwargs = build_asyncpg_engine_config(url)

        parsed = urlparse(normalized)
        query = parse_qs(parsed.query)
        self.assertNotIn("sslmode", query)
        self.assertNotIn("channel_binding", query)
        self.assertEqual(query["application_name"], ["crm"])

        context = kwargs["connect_args"]["ssl"]
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_sslmode_verify_ca_disables_hostname_check_only(self):
        url = "postgresql+asyncpg://user:pass@db.example.com/app?sslmode=verify-ca"

        _, kwargs = build_asyncpg_engine_config(url)

        context = kwargs["connect_args"]["ssl"]
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertFalse(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_pgbouncer_disables_sqlalchemy_and_asyncpg_statement_caches(self):
        url = (
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?pgbouncer=true&prepared_statement_cache_size=100&application_name=crm"
        )

        normalized, kwargs = build_asyncpg_engine_config(url)

        query = parse_qs(urlparse(normalized).query)
        self.assertNotIn("pgbouncer", query)
        self.assertEqual(query["application_name"], ["crm"])
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)

    def test_supabase_pooler_is_treated_as_pgbouncer_with_tls(self):
        url = (
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?sslmode=require"
        )

        normalized, kwargs = build_asyncpg_engine_config(url)

        query = parse_qs(urlparse(normalized).query)
        self.assertNotIn("sslmode", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)
        self.assertIsInstance(kwargs["connect_args"]["ssl"], ssl.SSLContext)


if __name__ == "__main__":
    unittest.main()
