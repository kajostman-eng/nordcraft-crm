import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.v1.endpoints.auth import bootstrap_admin
from app.core.config import settings
from app.models.models import User
from app.schemas.schemas import BootstrapAdminRequest


class FakeCountResult:
    def __init__(self, count):
        self.count = count

    def scalar(self):
        return self.count


class FakeSession:
    def __init__(self, users_count=0):
        self.users_count = users_count
        self.execute_count = 0
        self.added = None
        self.commit_count = 0
        self.refresh_count = 0

    async def execute(self, statement):
        self.execute_count += 1
        return FakeCountResult(self.users_count)

    def add(self, model):
        self.added = model

    async def commit(self):
        self.commit_count += 1

    async def refresh(self, model):
        self.refresh_count += 1


class BootstrapAdminTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_bootstrap_token = settings.BOOTSTRAP_TOKEN
        settings.BOOTSTRAP_TOKEN = "expected-token"

    def tearDown(self):
        settings.BOOTSTRAP_TOKEN = self.original_bootstrap_token

    async def test_bootstrap_rejects_missing_token_before_checking_users(self):
        db = FakeSession(users_count=0)
        payload = BootstrapAdminRequest(email="admin@example.com", password="secret")

        with self.assertRaises(HTTPException) as raised:
            await bootstrap_admin(payload, db=db, x_bootstrap_token=None)

        self.assertEqual(raised.exception.status_code, 403)
        self.assertEqual(raised.exception.detail, "Invalid bootstrap token")
        self.assertEqual(db.execute_count, 0)
        self.assertIsNone(db.added)

    async def test_bootstrap_creates_admin_when_token_matches_and_no_users_exist(self):
        db = FakeSession(users_count=0)
        payload = BootstrapAdminRequest(
            email="admin@example.com",
            password="secret",
            full_name="Admin User",
        )

        with patch("app.api.v1.endpoints.auth.hash_password", return_value="hashed-secret"):
            user = await bootstrap_admin(payload, db=db, x_bootstrap_token="expected-token")

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, payload.email)
        self.assertEqual(user.full_name, payload.full_name)
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_active)
        self.assertEqual(user.password_hash, "hashed-secret")
        self.assertEqual(db.execute_count, 1)
        self.assertIs(db.added, user)
        self.assertEqual(db.commit_count, 1)
        self.assertEqual(db.refresh_count, 1)


if __name__ == "__main__":
    unittest.main()
