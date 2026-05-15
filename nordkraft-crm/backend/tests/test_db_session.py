import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse


os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/nordkraft_crm",
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import session  # noqa: E402


class EngineConfigurationTests(unittest.TestCase):
    def _build_engine(self, database_url: str):
        with (
            patch.object(session.settings, "DATABASE_URL", database_url),
            patch.object(session, "create_async_engine") as create_async_engine,
        ):
            created = object()
            create_async_engine.return_value = created

            self.assertIs(session._engine(), created)
            return create_async_engine.call_args

    def test_supabase_pgbouncer_url_strips_rejected_params_and_disables_caches(self):
        call_args = self._build_engine(
            "postgresql+asyncpg://user:pass@aws-0-us.pooler.supabase.com:6543/postgres"
            "?sslmode=require&pgbouncer=true&connect_timeout=10"
        )

        args, kwargs = call_args
        parsed_url = urlparse(args[0])
        query = parse_qs(parsed_url.query)

        self.assertEqual(parsed_url.scheme, "postgresql+asyncpg")
        self.assertEqual(query, {"connect_timeout": ["10"]})
        self.assertEqual(
            kwargs,
            {
                "echo": False,
                "connect_args": {
                    "ssl": "require",
                    "prepared_statement_cache_size": 0,
                    "statement_cache_size": 0,
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
