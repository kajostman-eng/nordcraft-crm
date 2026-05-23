import unittest

from fastapi import HTTPException

from app.api.v1.endpoints import auth
from app.core.config import settings
from app.schemas.schemas import BootstrapAdminRequest


class _CountResult:
    def __init__(self, count: int):
        self.count = count

    def scalar(self):
        return self.count


class _FakeDb:
    async def execute(self, _stmt):
        return _CountResult(0)

    def add(self, _user):
        pass

    async def commit(self):
        pass

    async def refresh(self, _user):
        pass


class BootstrapAdminTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.original_bootstrap_token = settings.BOOTSTRAP_TOKEN

    async def asyncTearDown(self):
        settings.BOOTSTRAP_TOKEN = self.original_bootstrap_token

    async def test_bootstrap_requires_configured_token(self):
        settings.BOOTSTRAP_TOKEN = ""

        with self.assertRaises(HTTPException) as err:
            await auth.bootstrap_admin(
                BootstrapAdminRequest(email="admin@example.com", password="secret123"),
                bootstrap_token=None,
                db=_FakeDb(),
            )

        self.assertEqual(err.exception.status_code, 403)
        self.assertEqual(err.exception.detail, "Admin bootstrap is disabled")

    async def test_bootstrap_rejects_wrong_token(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"

        with self.assertRaises(HTTPException) as err:
            await auth.bootstrap_admin(
                BootstrapAdminRequest(email="admin@example.com", password="secret123"),
                bootstrap_token="wrong-token",
                db=_FakeDb(),
            )

        self.assertEqual(err.exception.status_code, 403)
        self.assertEqual(err.exception.detail, "Invalid bootstrap token")


if __name__ == "__main__":
    unittest.main()
