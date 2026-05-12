import ssl
import unittest
from unittest import mock

from app.db.session import _asyncpg_engine_options


class AsyncpgEngineOptionsTests(unittest.TestCase):
    def test_verify_full_sslmode_uses_verifying_context_and_strips_query(self):
        with mock.patch("ssl.SSLContext.load_verify_locations"):
            url, kwargs = _asyncpg_engine_options(
                "postgresql+asyncpg://u:p@db.example.com:5432/app"
                "?sslmode=verify-full&sslrootcert=/tmp/ca.pem&pgbouncer=true"
            )

        self.assertEqual(url, "postgresql+asyncpg://u:p@db.example.com:5432/app")
        connect_args = kwargs["connect_args"]
        self.assertEqual(connect_args["statement_cache_size"], 0)
        self.assertIsInstance(connect_args["ssl"], ssl.SSLContext)
        self.assertTrue(connect_args["ssl"].check_hostname)
        self.assertEqual(connect_args["ssl"].verify_mode, ssl.CERT_REQUIRED)

    def test_sslmode_disable_is_not_downgraded_to_asyncpg_default_prefer(self):
        url, kwargs = _asyncpg_engine_options(
            "postgresql+asyncpg://u:p@db.example.com:5432/app?sslmode=disable"
        )

        self.assertEqual(url, "postgresql+asyncpg://u:p@db.example.com:5432/app")
        self.assertIs(kwargs["connect_args"]["ssl"], False)

    def test_supabase_still_defaults_to_tls_required(self):
        url, kwargs = _asyncpg_engine_options(
            "postgresql+asyncpg://u:p@aws-0-us-east-1.pooler.supabase.com:5432/app"
        )

        self.assertEqual(url, "postgresql+asyncpg://u:p@aws-0-us-east-1.pooler.supabase.com:5432/app")
        self.assertEqual(kwargs["connect_args"]["ssl"], "require")


if __name__ == "__main__":
    unittest.main()
