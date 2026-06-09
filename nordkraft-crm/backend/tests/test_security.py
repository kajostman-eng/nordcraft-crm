import unittest

from app.core.security import hash_password, verify_password


class PasswordHashingTests(unittest.TestCase):
    def test_hash_password_round_trip_with_current_bcrypt(self):
        password_hash = hash_password("correct-horse-battery-staple")

        self.assertTrue(password_hash.startswith("$2b$"))
        self.assertTrue(verify_password("correct-horse-battery-staple", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))

    def test_verify_password_rejects_malformed_hash(self):
        self.assertFalse(verify_password("password", "not-a-bcrypt-hash"))


if __name__ == "__main__":
    unittest.main()
