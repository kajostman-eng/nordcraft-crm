from unittest import TestCase
from urllib.parse import parse_qs, urlparse

from app.db.url import normalize_asyncpg_url


class AsyncpgUrlTests(TestCase):
    def test_non_asyncpg_url_is_unchanged(self):
        url, connect_args = normalize_asyncpg_url("sqlite+aiosqlite:///local.db")

        self.assertEqual(url, "sqlite+aiosqlite:///local.db")
        self.assertEqual(connect_args, {})

    def test_sslmode_is_translated_to_connect_args(self):
        url, connect_args = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app?sslmode=require&application_name=crm"
        )

        self.assertEqual(connect_args, {"ssl": True})
        query = parse_qs(urlparse(url).query)
        self.assertNotIn("sslmode", query)
        self.assertEqual(query["application_name"], ["crm"])

    def test_supabase_pooler_disables_prepared_statement_caches(self):
        url, connect_args = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@aws-0.pooler.supabase.com:6543/postgres"
            "?sslmode=require&pgbouncer=true"
        )

        self.assertEqual(connect_args, {"ssl": True, "statement_cache_size": 0})
        query = parse_qs(urlparse(url).query)
        self.assertNotIn("sslmode", query)
        self.assertNotIn("pgbouncer", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])

    def test_pooler_keeps_existing_prepared_statement_cache_size(self):
        url, connect_args = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@db.example.com:6543/app"
            "?prepared_statement_cache_size=0"
        )

        self.assertEqual(connect_args, {"statement_cache_size": 0})
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
