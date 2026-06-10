import unittest

from fastapi import HTTPException

from app.api.v1.endpoints.auth import validate_bootstrap_token
from app.core.config import settings


class BootstrapTokenTest(unittest.TestCase):
    def setUp(self):
        self._original_token = settings.BOOTSTRAP_TOKEN

    def tearDown(self):
        settings.BOOTSTRAP_TOKEN = self._original_token

    def assert_forbidden(self, token):
        with self.assertRaises(HTTPException) as cm:
            validate_bootstrap_token(token)
        self.assertEqual(cm.exception.status_code, 403)

    def test_rejects_when_bootstrap_token_is_not_configured(self):
        settings.BOOTSTRAP_TOKEN = ""

        self.assert_forbidden("anything")

    def test_rejects_missing_or_wrong_bootstrap_token(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"

        self.assert_forbidden(None)
        self.assert_forbidden("wrong-token")

    def test_accepts_matching_bootstrap_token(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"

        validate_bootstrap_token("expected-token")


if __name__ == "__main__":
    unittest.main()
