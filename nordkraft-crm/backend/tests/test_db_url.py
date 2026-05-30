import unittest
from urllib.parse import parse_qs, urlparse

from app.db.url import make_asyncpg_url_and_kwargs


class AsyncpgUrlTests(unittest.TestCase):
    def test_supabase_pooler_strips_libpq_ssl_and_disables_prepared_cache(self):
        url, kwargs = make_asyncpg_url_and_kwargs(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?sslmode=require&channel_binding=require"
        )

        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        self.assertNotIn("sslmode", query)
        self.assertNotIn("channel_binding", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"], {"ssl": "require"})

    def test_pgbouncer_flag_is_stripped_but_enables_prepared_cache_disable(self):
        url, kwargs = make_asyncpg_url_and_kwargs(
            "postgresql+asyncpg://user:pass@db.example.com/app?pgbouncer=true&ssl=true&app_name=crm"
        )

        query = parse_qs(urlparse(url).query)
        self.assertNotIn("pgbouncer", query)
        self.assertNotIn("ssl", query)
        self.assertEqual(query["app_name"], ["crm"])
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"], {"ssl": "require"})

    def test_plain_asyncpg_url_is_not_marked_as_pooler(self):
        url, kwargs = make_asyncpg_url_and_kwargs(
            "postgresql+asyncpg://user:pass@db.example.com:5432/app?application_name=crm"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["application_name"], ["crm"])
        self.assertNotIn("prepared_statement_cache_size", query)
        self.assertEqual(kwargs, {"echo": False})


if __name__ == "__main__":
    unittest.main()
