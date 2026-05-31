from unittest import TestCase

from app.core.security import hash_password, verify_password


class PasswordHashingTests(TestCase):
    def test_hash_password_generates_verifiable_bcrypt_hash(self):
        password_hash = hash_password("correct horse battery staple")

        self.assertTrue(password_hash.startswith("$2"))
        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("wrong password", password_hash))
