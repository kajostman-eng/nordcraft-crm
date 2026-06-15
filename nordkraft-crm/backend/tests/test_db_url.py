import ssl
import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import asyncpg_engine_options


class AsyncpgEngineOptionsTests(unittest.TestCase):
    def test_strips_libpq_sslmode_and_enables_tls(self):
        url, kwargs = asyncpg_engine_options(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app?sslmode=require"
        )

        self.assertNotIn("sslmode", parse_qs(urlparse(url).query))
        context = kwargs["connect_args"]["ssl"]
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertFalse(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_NONE)

    def test_preserves_verify_full_certificate_checks(self):
        _, kwargs = asyncpg_engine_options(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app?sslmode=verify-full"
        )

        context = kwargs["connect_args"]["ssl"]
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_detects_supabase_pooler_without_explicit_pgbouncer_flag(self):
        url, kwargs = asyncpg_engine_options(
            "postgresql+asyncpg://user:pass@aws-0.pooler.supabase.com:6543/postgres?sslmode=require"
        )

        query = parse_qs(urlparse(url).query)
        connect_args = kwargs["connect_args"]
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertNotIn("sslmode", query)
        self.assertEqual(connect_args["statement_cache_size"], 0)
        self.assertTrue(callable(connect_args["prepared_statement_name_func"]))

    def test_keeps_non_asyncpg_urls_unchanged(self):
        raw = "sqlite+aiosqlite:///tmp/test.db"

        url, kwargs = asyncpg_engine_options(raw)

        self.assertEqual(url, raw)
        self.assertEqual(kwargs, {"echo": False})


if __name__ == "__main__":
    unittest.main()
