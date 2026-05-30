import unittest

from fastapi import HTTPException

from app.api.v1.endpoints import auth
from app.core.config import settings
from app.schemas.schemas import BootstrapAdminRequest


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class _FakeDb:
    def __init__(self, users_count=0):
        self.users_count = users_count
        self.added = None
        self.committed = False
        self.refreshed = False

    async def execute(self, _statement):
        return _ScalarResult(self.users_count)

    def add(self, user):
        self.added = user

    async def commit(self):
        self.committed = True

    async def refresh(self, _user):
        self.refreshed = True


class BootstrapAdminTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._old_bootstrap_token = settings.BOOTSTRAP_TOKEN

    def tearDown(self):
        settings.BOOTSTRAP_TOKEN = self._old_bootstrap_token

    async def test_bootstrap_requires_configured_token(self):
        settings.BOOTSTRAP_TOKEN = ""
        db = _FakeDb()
        payload = BootstrapAdminRequest(email="admin@example.com", password="secret123")

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(payload, x_bootstrap_token="anything", db=db)

        self.assertEqual(exc.exception.status_code, 503)
        self.assertIsNone(db.added)

    async def test_bootstrap_rejects_missing_or_wrong_token(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"
        payload = BootstrapAdminRequest(email="admin@example.com", password="secret123")

        for token in (None, "wrong-token"):
            db = _FakeDb()
            with self.assertRaises(HTTPException) as exc:
                await auth.bootstrap_admin(payload, x_bootstrap_token=token, db=db)

            self.assertEqual(exc.exception.status_code, 403)
            self.assertIsNone(db.added)

    async def test_bootstrap_creates_admin_with_matching_token(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb()
        payload = BootstrapAdminRequest(
            email="admin@example.com",
            password="secret123",
            full_name="Admin User",
        )

        user = await auth.bootstrap_admin(payload, x_bootstrap_token="expected-token", db=db)

        self.assertIs(user, db.added)
        self.assertEqual(user.email, "admin@example.com")
        self.assertEqual(user.full_name, "Admin User")
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_active)
        self.assertTrue(user.password_hash)
        self.assertTrue(db.committed)
        self.assertTrue(db.refreshed)


if __name__ == "__main__":
    unittest.main()
