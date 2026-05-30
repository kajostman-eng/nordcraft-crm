import unittest

from app.core.security import hash_password, verify_password


class PasswordSecurityTests(unittest.TestCase):
    def test_hash_and_verify_password(self):
        hashed = hash_password("secret123")

        self.assertNotEqual(hashed, "secret123")
        self.assertTrue(verify_password("secret123", hashed))
        self.assertFalse(verify_password("wrong", hashed))


if __name__ == "__main__":
    unittest.main()
