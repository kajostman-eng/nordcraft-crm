import unittest

from app.db.url import normalize_asyncpg_url


class NormalizeAsyncpgUrlTests(unittest.TestCase):
    def test_supabase_pooler_enables_ssl_and_disables_statement_caches(self):
        config = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?sslmode=require&pgbouncer=true"
        )

        self.assertEqual(
            config.url,
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?prepared_statement_cache_size=0",
        )
        self.assertTrue(config.uses_external_pooler)
        self.assertIs(config.connect_args["ssl"], True)
        self.assertEqual(config.connect_args["statement_cache_size"], 0)
        self.assertTrue(callable(config.connect_args["prepared_statement_name_func"]))

    def test_pooler_host_does_not_require_query_flag(self):
        config = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com/postgres"
            "?sslmode=require"
        )

        self.assertTrue(config.uses_external_pooler)
        self.assertIn("prepared_statement_cache_size=0", config.url)
        self.assertEqual(config.connect_args["statement_cache_size"], 0)

    def test_non_pooler_preserves_supported_query_parameters(self):
        config = normalize_asyncpg_url(
            "postgresql+asyncpg://user:pass@db.example.com/app?application_name=crm"
        )

        self.assertEqual(
            config.url,
            "postgresql+asyncpg://user:pass@db.example.com/app?application_name=crm",
        )
        self.assertFalse(config.uses_external_pooler)
        self.assertEqual(config.connect_args, {})


if __name__ == "__main__":
    unittest.main()
