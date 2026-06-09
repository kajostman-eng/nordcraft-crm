import unittest

from fastapi import HTTPException

from app.api.v1.endpoints import auth as auth_endpoint
from app.api.v1.endpoints.auth import bootstrap_admin
from app.core.config import settings
from app.schemas.schemas import BootstrapAdminRequest


class FailingSession:
    async def execute(self, *_args, **_kwargs):
        raise AssertionError("bootstrap should reject before querying the database")


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class CountingSession:
    def __init__(self, count):
        self.count = count
        self.added = None
        self.committed = False
        self.refreshed = None

    async def execute(self, *_args, **_kwargs):
        return ScalarResult(self.count)

    def add(self, user):
        self.added = user

    async def commit(self):
        self.committed = True

    async def refresh(self, user):
        self.refreshed = user


class BootstrapAdminTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.previous_token = settings.BOOTSTRAP_TOKEN
        self.previous_hash_password = auth_endpoint.hash_password
        self.payload = BootstrapAdminRequest(
            email="admin@example.com",
            password="correct-horse-battery-staple",
            full_name="Admin User",
        )

    def tearDown(self):
        settings.BOOTSTRAP_TOKEN = self.previous_token
        auth_endpoint.hash_password = self.previous_hash_password

    async def test_rejects_bootstrap_when_token_not_configured(self):
        settings.BOOTSTRAP_TOKEN = ""

        with self.assertRaises(HTTPException) as raised:
            await bootstrap_admin(self.payload, FailingSession(), x_bootstrap_token=None)

        self.assertEqual(raised.exception.status_code, 503)

    async def test_rejects_bootstrap_when_token_is_missing_or_wrong(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"

        for submitted_token in (None, "", "wrong-token"):
            with self.subTest(submitted_token=submitted_token):
                with self.assertRaises(HTTPException) as raised:
                    await bootstrap_admin(self.payload, FailingSession(), x_bootstrap_token=submitted_token)

                self.assertEqual(raised.exception.status_code, 403)

    async def test_valid_token_still_rejects_after_bootstrap_completed(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"

        with self.assertRaises(HTTPException) as raised:
            await bootstrap_admin(self.payload, CountingSession(count=1), x_bootstrap_token="expected-token")

        self.assertEqual(raised.exception.status_code, 403)
        self.assertEqual(raised.exception.detail, "Bootstrap already completed")

    async def test_valid_token_creates_first_admin(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"
        auth_endpoint.hash_password = lambda password: f"hashed:{password}"
        session = CountingSession(count=0)

        user = await bootstrap_admin(self.payload, session, x_bootstrap_token="expected-token")

        self.assertIs(session.added, user)
        self.assertTrue(session.committed)
        self.assertIs(session.refreshed, user)
        self.assertEqual(user.email, "admin@example.com")
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_active)
        self.assertEqual(user.password_hash, "hashed:correct-horse-battery-staple")


if __name__ == "__main__":
    unittest.main()
