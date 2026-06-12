import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.v1.endpoints import auth
from app.schemas.schemas import BootstrapAdminRequest


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar(self):
        return self._value


class _FakeDb:
    def __init__(self, users_count=0):
        self.users_count = users_count
        self.added_user = None
        self.committed = False
        self.refreshed = False

    async def execute(self, _statement):
        return _ScalarResult(self.users_count)

    def add(self, user):
        self.added_user = user

    async def commit(self):
        self.committed = True

    async def refresh(self, _user):
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

    async def test_rejects_missing_bootstrap_token_when_no_users_exist(self):
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb(users_count=0)

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(self.payload, x_bootstrap_token=None, db=db)

        self.assertEqual(exc.exception.status_code, 403)
        self.assertIsNone(db.added_user)
        self.assertFalse(db.committed)

    async def test_rejects_when_bootstrap_token_is_not_configured(self):
        auth.settings.BOOTSTRAP_TOKEN = ""
        db = _FakeDb(users_count=0)

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(self.payload, x_bootstrap_token="anything", db=db)

        self.assertEqual(exc.exception.status_code, 503)
        self.assertIsNone(db.added_user)
        self.assertFalse(db.committed)

    async def test_rejects_wrong_bootstrap_token(self):
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb(users_count=0)

        with self.assertRaises(HTTPException) as exc:
            await auth.bootstrap_admin(self.payload, x_bootstrap_token="wrong-token", db=db)

        self.assertEqual(exc.exception.status_code, 403)
        self.assertIsNone(db.added_user)
        self.assertFalse(db.committed)

    async def test_accepts_matching_bootstrap_token_for_first_admin(self):
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        db = _FakeDb(users_count=0)

        with patch.object(auth, "hash_password", return_value="hashed-password"):
            user = await auth.bootstrap_admin(
                self.payload,
                x_bootstrap_token="expected-token",
                db=db,
            )

        self.assertIs(user, db.added_user)
        self.assertTrue(db.committed)
        self.assertTrue(db.refreshed)
        self.assertEqual(user.email, self.payload.email)
        self.assertEqual(user.full_name, self.payload.full_name)
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_active)
        self.assertEqual(user.password_hash, "hashed-password")


if __name__ == "__main__":
    unittest.main()
