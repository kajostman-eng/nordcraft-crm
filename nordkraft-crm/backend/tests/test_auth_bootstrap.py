import asyncio
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.v1.endpoints import auth
from app.schemas.schemas import BootstrapAdminRequest


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class _FakeDb:
    def __init__(self, users_count=0):
        self.users_count = users_count
        self.added_user = None
        self.committed = False
        self.refreshed_user = None
        self.executed = False

    async def execute(self, _statement):
        self.executed = True
        return _ScalarResult(self.users_count)

    def add(self, user):
        self.added_user = user

    async def commit(self):
        self.committed = True

    async def refresh(self, user):
        self.refreshed_user = user


class BootstrapAdminTests(unittest.TestCase):
    def test_bootstrap_rejects_missing_configured_token(self):
        payload = BootstrapAdminRequest(email="admin@example.com", password="secret123")
        db = _FakeDb()

        with patch.object(auth.settings, "BOOTSTRAP_TOKEN", "expected"):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(auth.bootstrap_admin(payload, bootstrap_token=None, db=db))

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertFalse(db.executed)

    def test_bootstrap_rejects_when_token_is_not_configured(self):
        payload = BootstrapAdminRequest(email="admin@example.com", password="secret123")
        db = _FakeDb()

        with patch.object(auth.settings, "BOOTSTRAP_TOKEN", ""):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(auth.bootstrap_admin(payload, bootstrap_token="anything", db=db))

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertFalse(db.executed)

    def test_bootstrap_creates_admin_with_matching_token(self):
        payload = BootstrapAdminRequest(
            email="admin@example.com",
            password="secret123",
            full_name="Admin User",
        )
        db = _FakeDb()

        with patch.object(auth.settings, "BOOTSTRAP_TOKEN", "expected"):
            with patch.object(auth, "hash_password", return_value="hashed-password"):
                user = asyncio.run(auth.bootstrap_admin(payload, bootstrap_token="expected", db=db))

        self.assertIs(user, db.added_user)
        self.assertTrue(db.committed)
        self.assertIs(db.refreshed_user, user)
        self.assertEqual(user.email, "admin@example.com")
        self.assertEqual(user.role, "admin")
        self.assertEqual(user.password_hash, "hashed-password")

    def test_bootstrap_still_blocks_after_first_user_exists(self):
        payload = BootstrapAdminRequest(email="admin@example.com", password="secret123")
        db = _FakeDb(users_count=1)

        with patch.object(auth.settings, "BOOTSTRAP_TOKEN", "expected"):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(auth.bootstrap_admin(payload, bootstrap_token="expected", db=db))

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIsNone(db.added_user)


if __name__ == "__main__":
    unittest.main()
