"""Unit tests: password hashing and tokens (no database)."""

import unittest

import jwt

from app.config import get_settings
from app.utilities.security import create_access_token, encrypt_password, verify_password


class SecurityUnitTests(unittest.TestCase):

    def test_password_hash(self):
        hashed = encrypt_password("mypass")
        self.assertNotEqual(hashed, "mypass")

    def test_check_password(self):
        hashed = encrypt_password("mypass")
        self.assertTrue(verify_password("mypass", hashed))
        self.assertFalse(verify_password("wrongpass", hashed))

    def test_access_token(self):
        token = create_access_token({"sub": "9", "role": "admin"})
        settings = get_settings()
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        self.assertEqual(data["sub"], "9")
        self.assertEqual(data["role"], "admin")
        self.assertIn("exp", data)
