from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from app.db import session


def _build_engine_url(raw_url: str):
    with patch.object(session.settings, "DATABASE_URL", raw_url), patch.object(
        session, "create_async_engine"
    ) as create_async_engine:
        session._engine()
    return create_async_engine.call_args.args[0], create_async_engine.call_args.kwargs


class SessionEngineConfigTests(TestCase):
    def test_pgbouncer_disables_asyncpg_and_sqlalchemy_statement_caches(self):
        url, kwargs = _build_engine_url(
            "postgresql+asyncpg://user:pass@db.pooler.supabase.com:6543/postgres"
            "?sslmode=require&pgbouncer=true&application_name=crm"
        )

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        self.assertNotIn("sslmode", query)
        self.assertNotIn("pgbouncer", query)
        self.assertEqual(query["application_name"], ["crm"])
        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)

    def test_pgbouncer_overrides_existing_prepared_statement_cache_size(self):
        url, _kwargs = _build_engine_url(
            "postgresql+asyncpg://user:pass@example.pooler.supabase.com/postgres"
            "?pgbouncer=1&prepared_statement_cache_size=100"
        )

        query = parse_qs(urlparse(url).query)

        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
