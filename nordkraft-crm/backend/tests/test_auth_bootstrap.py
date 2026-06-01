import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.v1.endpoints import auth
from app.schemas.schemas import BootstrapAdminRequest


class _CountResult:
    def __init__(self, count: int):
        self.count = count

    def scalar(self):
        return self.count


class _FakeDb:
    def __init__(self, users_count: int = 0):
        self.users_count = users_count
        self.executed = False
        self.added = None
        self.committed = False
        self.refreshed = False

    async def execute(self, statement):
        self.executed = True
        return _CountResult(self.users_count)

    def add(self, user):
        self.added = user

    async def commit(self):
        self.committed = True

    async def refresh(self, user):
        self.refreshed = True


class BootstrapAdminTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._original_bootstrap_token = auth.settings.BOOTSTRAP_TOKEN
        self.payload = BootstrapAdminRequest(
            email="admin@example.com",
            password="correct horse battery staple",
            full_name="Admin User",
        )

    def tearDown(self):
        auth.settings.BOOTSTRAP_TOKEN = self._original_bootstrap_token

    async def test_rejects_missing_bootstrap_token_before_querying_users(self):
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb()

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(self.payload, db=db, bootstrap_token=None)

        self.assertEqual(exc.exception.status_code, 401)
        self.assertFalse(db.executed)
        self.assertIsNone(db.added)

    async def test_rejects_unconfigured_bootstrap_token_before_querying_users(self):
        auth.settings.BOOTSTRAP_TOKEN = ""
        db = _FakeDb()

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(self.payload, db=db, bootstrap_token="anything")

        self.assertEqual(exc.exception.status_code, 503)
        self.assertFalse(db.executed)
        self.assertIsNone(db.added)

    async def test_rejects_bootstrap_when_users_exist(self):
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb(users_count=1)

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(self.payload, db=db, bootstrap_token="expected-token")

        self.assertEqual(exc.exception.status_code, 403)
        self.assertTrue(db.executed)
        self.assertIsNone(db.added)

    async def test_creates_first_admin_with_valid_bootstrap_token(self):
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb()

        with patch.object(auth, "hash_password", return_value="hashed-password"):
            user = await auth.bootstrap_admin(
                self.payload,
                db=db,
                bootstrap_token="expected-token",
            )

        self.assertEqual(user.email, "admin@example.com")
        self.assertEqual(user.role, "admin")
        self.assertEqual(user.password_hash, "hashed-password")
        self.assertIs(db.added, user)
        self.assertTrue(db.committed)
        self.assertTrue(db.refreshed)


if __name__ == "__main__":
    unittest.main()
