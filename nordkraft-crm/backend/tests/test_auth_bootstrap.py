from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.v1.endpoints import auth
from app.main import app


class _CountResult:
    def __init__(self, count: int):
        self._count = count

    def scalar(self) -> int:
        return self._count


class _FakeDb:
    def __init__(self, user_count: int = 0):
        self.user_count = user_count
        self.added_user = None
        self.committed = False

    async def execute(self, _statement):
        return _CountResult(self.user_count)

    def add(self, user):
        self.added_user = user

    async def commit(self):
        self.committed = True

    async def refresh(self, user):
        user.id = user.id or "user-1"
        user.created_at = user.created_at or datetime(2026, 1, 1)


class BootstrapAdminTests(TestCase):
    def setUp(self):
        self.original_bootstrap_token = auth.settings.BOOTSTRAP_TOKEN
        auth.settings.BOOTSTRAP_TOKEN = "expected-token"
        self.db = _FakeDb()

        async def override_get_db():
            yield self.db

        app.dependency_overrides[auth.get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        auth.settings.BOOTSTRAP_TOKEN = self.original_bootstrap_token

    def _post_bootstrap(self, headers=None):
        return self.client.post(
            "/api/v1/auth/bootstrap",
            json={
                "email": "admin@example.com",
                "password": "correct horse battery staple",
                "full_name": "Admin User",
            },
            headers=headers or {},
        )

    def test_bootstrap_requires_token_header(self):
        response = self._post_bootstrap()

        self.assertEqual(response.status_code, 403)
        self.assertIsNone(self.db.added_user)
        self.assertFalse(self.db.committed)

    def test_bootstrap_rejects_wrong_token(self):
        response = self._post_bootstrap(headers={"X-Bootstrap-Token": "wrong-token"})

        self.assertEqual(response.status_code, 403)
        self.assertIsNone(self.db.added_user)
        self.assertFalse(self.db.committed)

    def test_bootstrap_fails_closed_when_token_is_not_configured(self):
        auth.settings.BOOTSTRAP_TOKEN = ""

        response = self._post_bootstrap(headers={"X-Bootstrap-Token": "anything"})

        self.assertEqual(response.status_code, 403)
        self.assertIsNone(self.db.added_user)
        self.assertFalse(self.db.committed)

    def test_bootstrap_allows_matching_token(self):
        with patch.object(auth, "hash_password", return_value="hashed-password"):
            response = self._post_bootstrap(headers={"X-Bootstrap-Token": "expected-token"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["role"], "admin")
        self.assertEqual(self.db.added_user.email, "admin@example.com")
        self.assertEqual(self.db.added_user.password_hash, "hashed-password")
        self.assertTrue(self.db.committed)
