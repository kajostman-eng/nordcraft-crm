import importlib
import os
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse


class SessionEngineTests(unittest.TestCase):
    def _load_session_with_url(self, database_url: str):
        for module_name in ("app.db.session", "app.core.config"):
            sys.modules.pop(module_name, None)

        with patch.dict(os.environ, {"DATABASE_URL": database_url}, clear=False):
            with patch("sqlalchemy.ext.asyncio.create_async_engine") as create_engine:
                with patch("sqlalchemy.ext.asyncio.async_sessionmaker"):
                    importlib.import_module("app.db.session")

        return create_engine.call_args

    def test_pgbouncer_disables_sqlalchemy_prepared_statement_cache(self):
        call_args = self._load_session_with_url(
            "postgresql+asyncpg://user:pass@aws-0-eu.pooler.supabase.com:6543/db"
            "?sslmode=require&pgbouncer=true&application_name=nordkraft"
        )

        args, kwargs = call_args
        parsed = urlparse(args[0])
        query = parse_qs(parsed.query)

        self.assertEqual(query["prepared_statement_cache_size"], ["0"])
        self.assertEqual(query["application_name"], ["nordkraft"])
        self.assertNotIn("sslmode", query)
        self.assertNotIn("pgbouncer", query)
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")
        self.assertEqual(kwargs["connect_args"]["statement_cache_size"], 0)

    def test_pgbouncer_overrides_existing_prepared_statement_cache_size(self):
        call_args = self._load_session_with_url(
            "postgresql+asyncpg://user:pass@db.example.com:5432/db"
            "?pgbouncer=1&prepared_statement_cache_size=100"
        )

        args, _ = call_args
        query = parse_qs(urlparse(args[0]).query)

        self.assertEqual(query["prepared_statement_cache_size"], ["0"])

    def test_ssl_query_keys_are_stripped_after_connect_args_are_set(self):
        call_args = self._load_session_with_url(
            "postgresql+asyncpg://user:pass@db.supabase.co:5432/db"
            "?sslmode=require&sslrootcert=/tmp/root.crt&application_name=nordkraft"
        )

        args, kwargs = call_args
        query = parse_qs(urlparse(args[0]).query)

        self.assertEqual(query, {"application_name": ["nordkraft"]})
        self.assertEqual(kwargs["connect_args"], {"ssl": "require"})


if __name__ == "__main__":
    unittest.main()
