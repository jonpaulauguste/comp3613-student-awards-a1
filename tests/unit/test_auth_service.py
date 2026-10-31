"""Unit tests: AuthService with a mocked user repository (no database)."""

import unittest
from unittest.mock import MagicMock

import jwt

from app.config import get_settings
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.errors import ConflictError, InvalidInputError
from app.utilities.security import encrypt_password


def make_service():
    user_repo = MagicMock()
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None
    user_repo.create.side_effect = lambda new_user: new_user
    return AuthService(user_repo), user_repo


def bob():
    return User(
        id=5,
        username="bob",
        email="bob@example.com",
        password=encrypt_password("bobpass"),
        role="regular_user",
    )


class AuthServiceUnitTests(unittest.TestCase):

    def setUp(self):
        self.service, self.user_repo = make_service()

    def test_authenticate_user(self):
        self.user_repo.get_by_username.return_value = bob()
        token = self.service.authenticate_user("bob", "bobpass")
        settings = get_settings()
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        self.assertEqual(data["sub"], "5")
        self.assertEqual(data["role"], "regular_user")

    def test_authenticate_wrong_password(self):
        self.user_repo.get_by_username.return_value = bob()
        self.assertIsNone(self.service.authenticate_user("bob", "wrongpass"))

    def test_authenticate_unknown_user(self):
        self.assertIsNone(self.service.authenticate_user("ghost", "bobpass"))

    def test_register_user(self):
        new_user = self.service.register_user("carl", "carl@example.com", "secret1")
        self.assertEqual(new_user.username, "carl")
        self.assertEqual(new_user.role, "regular_user")
        self.assertNotEqual(new_user.password, "secret1")

    def test_register_duplicate_username(self):
        self.user_repo.get_by_username.return_value = bob()
        with self.assertRaises(ConflictError):
            self.service.register_user("bob", "other@example.com", "secret1")
        self.user_repo.create.assert_not_called()

    def test_register_duplicate_email(self):
        self.user_repo.get_by_email.return_value = bob()
        with self.assertRaises(ConflictError):
            self.service.register_user("newbie", "bob@example.com", "secret1")
        self.user_repo.create.assert_not_called()

    def test_register_short_password(self):
        with self.assertRaises(InvalidInputError):
            self.service.register_user("carl", "carl@example.com", "123")
        self.user_repo.create.assert_not_called()
