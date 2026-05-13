import unittest
from urllib.parse import parse_qs, urlparse

from sqlalchemy.pool import NullPool

from app.db.session import _engine_options


class EngineOptionsTest(unittest.TestCase):
    def test_pgbouncer_url_disables_all_prepared_statement_caches(self):
        url, kwargs = _engine_options(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/postgres"
            "?sslmode=require&pgbouncer=true"
        )

        self.assertEqual(parse_qs(urlparse(url).query), {})
        self.assertIs(kwargs["poolclass"], NullPool)

        connect_args = kwargs["connect_args"]
        self.assertEqual(connect_args["ssl"], "require")
        self.assertEqual(connect_args["statement_cache_size"], 0)
        self.assertEqual(connect_args["prepared_statement_cache_size"], 0)
        self.assertNotEqual(
            connect_args["prepared_statement_name_func"](),
            connect_args["prepared_statement_name_func"](),
        )

    def test_asyncpg_rejected_query_keys_are_stripped_but_other_options_remain(self):
        url, kwargs = _engine_options(
            "postgresql+asyncpg://user:pass@db.example.com/app"
            "?sslmode=require&pgbouncer=1&application_name=nordkraft"
        )

        query = parse_qs(urlparse(url).query)
        self.assertEqual(query, {"application_name": ["nordkraft"]})
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(kwargs["connect_args"]["prepared_statement_cache_size"], 0)


if __name__ == "__main__":
    unittest.main()
