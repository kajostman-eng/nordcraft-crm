import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import prepare_asyncpg_url


class PrepareAsyncpgUrlTests(unittest.TestCase):
    def test_rewrites_railway_postgresql_url_and_strips_sslmode(self):
        url, connect_args = prepare_asyncpg_url(
            "postgresql://user:pass@railway.internal:5432/app?sslmode=require"
        )

        parsed = urlparse(url)
        self.assertEqual(parsed.scheme, "postgresql+asyncpg")
        self.assertEqual(parse_qs(parsed.query), {})
        self.assertEqual(connect_args, {"ssl": True})

    def test_rewrites_legacy_postgres_url(self):
        url, connect_args = prepare_asyncpg_url("postgres://user:pass@localhost/app")

        self.assertEqual(url, "postgresql+asyncpg://user:pass@localhost/app")
        self.assertEqual(connect_args, {})

    def test_supabase_pooler_disables_prepared_statement_caches(self):
        url, connect_args = prepare_asyncpg_url(
            "postgresql://user:pass@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
        )

        query = parse_qs(urlparse(url).query)
        self.assertNotIn("sslmode", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(connect_args, {"ssl": True, "statement_cache_size": 0})

    def test_explicit_pgbouncer_flag_is_not_forwarded_to_asyncpg(self):
        url, connect_args = prepare_asyncpg_url(
            "postgresql+asyncpg://user:pass@db.example.com/app?pgbouncer=true&application_name=crm"
        )

        query = parse_qs(urlparse(url).query)
        self.assertNotIn("pgbouncer", query)
        self.assertEqual(query["application_name"], ["crm"])
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(connect_args, {"statement_cache_size": 0})


if __name__ == "__main__":
    unittest.main()
