import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.v1.endpoints.auth import bootstrap_admin
from app.schemas.schemas import BootstrapAdminRequest


class RejectingSession:
    async def execute(self, _statement):
        raise AssertionError("bootstrap token must be checked before database access")


class AuthBootstrapTest(unittest.IsolatedAsyncioTestCase):
    async def test_bootstrap_requires_configured_header_token(self):
        payload = BootstrapAdminRequest(
            email="admin@example.com",
            password="correct-horse-battery-staple",
            full_name="Admin",
        )

        with patch("app.api.v1.endpoints.auth.settings.BOOTSTRAP_TOKEN", "expected-token"):
            with self.assertRaises(HTTPException) as exc:
                await bootstrap_admin(payload, bootstrap_token=None, db=RejectingSession())

        self.assertEqual(exc.exception.status_code, 403)
        self.assertEqual(exc.exception.detail, "Invalid bootstrap token")


if __name__ == "__main__":
    unittest.main()
