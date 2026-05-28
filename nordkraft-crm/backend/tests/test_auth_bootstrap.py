import asyncio
import unittest

from fastapi import HTTPException

from app.api.v1.endpoints.auth import bootstrap_admin
from app.core.config import settings


class BootstrapAdminTests(unittest.TestCase):
    def setUp(self):
        self.original_token = settings.BOOTSTRAP_TOKEN

    def tearDown(self):
        settings.BOOTSTRAP_TOKEN = self.original_token

    def test_bootstrap_rejects_when_token_is_not_configured(self):
        settings.BOOTSTRAP_TOKEN = ""

        with self.assertRaises(HTTPException) as exc:
            asyncio.run(bootstrap_admin(object(), x_bootstrap_token=None, db=None))

        self.assertEqual(exc.exception.status_code, 503)

    def test_bootstrap_rejects_wrong_token_before_touching_db(self):
        settings.BOOTSTRAP_TOKEN = "expected-token"

        with self.assertRaises(HTTPException) as exc:
            asyncio.run(bootstrap_admin(object(), x_bootstrap_token="wrong-token", db=None))

        self.assertEqual(exc.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
