import unittest

from app.core.security import hash_password, verify_password


class PasswordHashingTests(unittest.TestCase):
    def test_hash_password_produces_verifiable_bcrypt_hash(self):
        password_hash = hash_password("correct horse battery staple")

        self.assertTrue(password_hash.startswith("$2"))
        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("wrong password", password_hash))

    def test_verify_password_returns_false_for_invalid_hash(self):
        self.assertFalse(verify_password("password", "not-a-bcrypt-hash"))

    def test_verify_password_returns_false_for_password_over_bcrypt_limit(self):
        password_hash = hash_password("short password")

        self.assertFalse(verify_password("a" * 73, password_hash))

    def test_hash_password_rejects_password_over_bcrypt_limit(self):
        with self.assertRaises(ValueError):
            hash_password("a" * 73)


if __name__ == "__main__":
    unittest.main()
