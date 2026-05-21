from urllib.parse import parse_qs, urlparse
import unittest

from app.db.session import _normalized_asyncpg_engine_config


class AsyncpgEngineConfigTests(unittest.TestCase):
    def test_supabase_pooler_forces_sqlalchemy_prepared_statement_cache_off(self):
        url, engine_kwargs = _normalized_asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
            "?sslmode=require"
        )

        query = parse_qs(urlparse(url).query)

        self.assertNotIn("sslmode", query)
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(engine_kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(engine_kwargs["connect_args"]["statement_cache_size"], 0)

    def test_explicit_pgbouncer_flag_forces_prepared_statement_cache_off(self):
        url, engine_kwargs = _normalized_asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@db.example.com/app?pgbouncer=true&application_name=crm"
        )

        query = parse_qs(urlparse(url).query)

        self.assertNotIn("pgbouncer", query)
        self.assertEqual(query["application_name"], ["crm"])
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(engine_kwargs["connect_args"]["statement_cache_size"], 0)

    def test_pgbouncer_overrides_unsafe_user_prepared_statement_cache_size(self):
        url, _ = _normalized_asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?pgbouncer=1&prepared_statement_cache_size=100"
        )

        query = parse_qs(urlparse(url).query)

        self.assertEqual(query["prepared_statement_cache_size"], ["0"])

    def test_regular_asyncpg_url_preserves_safe_query_options(self):
        url, engine_kwargs = _normalized_asyncpg_engine_config(
            "postgresql+asyncpg://user:pass@db.example.com/app?application_name=crm"
        )

        query = parse_qs(urlparse(url).query)

        self.assertEqual(query, {"application_name": ["crm"]})
        self.assertEqual(engine_kwargs, {"echo": False})


if __name__ == "__main__":
    unittest.main()
