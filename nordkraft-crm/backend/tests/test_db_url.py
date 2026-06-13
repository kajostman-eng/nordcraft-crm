import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import normalize_asyncpg_url


class AsyncpgUrlTests(unittest.TestCase):
    def test_supabase_pooler_enables_tls_and_disables_prepared_statement_caches(self):
        url = (
            "postgresql+asyncpg://user:pass@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
            "?sslmode=require"
        )

        normalized, connect_args = normalize_asyncpg_url(url)

        parsed = urlparse(normalized)
        self.assertEqual(connect_args["ssl"], "require")
        self.assertEqual(connect_args["statement_cache_size"], 0)
        self.assertNotIn("sslmode", parse_qs(parsed.query))
        self.assertEqual(parse_qs(parsed.query)["prepared_statement_cache_size"], ["0"])

    def test_pgbouncer_flag_is_removed_after_disabling_caches(self):
        url = "postgresql+asyncpg://user:pass@db.example.com/postgres?pgbouncer=true&ssl=true"

        normalized, connect_args = normalize_asyncpg_url(url)

        query = parse_qs(urlparse(normalized).query)
        self.assertEqual(connect_args, {"ssl": "require", "statement_cache_size": 0})
        self.assertNotIn("pgbouncer", query)
        self.assertNotIn("ssl", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])

    def test_regular_supabase_url_keeps_statement_cache_enabled(self):
        url = "postgresql+asyncpg://user:pass@db.project.supabase.co/postgres?sslmode=require"

        normalized, connect_args = normalize_asyncpg_url(url)

        self.assertEqual(connect_args, {"ssl": "require"})
        self.assertNotIn("prepared_statement_cache_size", parse_qs(urlparse(normalized).query))

    def test_non_asyncpg_url_is_unchanged(self):
        url = "sqlite+aiosqlite:///tmp/test.db"

        normalized, connect_args = normalize_asyncpg_url(url)

        self.assertEqual(normalized, url)
        self.assertEqual(connect_args, {})


if __name__ == "__main__":
    unittest.main()
