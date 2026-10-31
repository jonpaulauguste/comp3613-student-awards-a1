"""Unit tests: AuthService with a mocked user repository (no database)."""

from unittest.mock import MagicMock

import jwt
import pytest

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


def test_authenticate_user():
    service, user_repo = make_service()
    user_repo.get_by_username.return_value = bob()
    token = service.authenticate_user("bob", "bobpass")
    settings = get_settings()
    data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    assert data["sub"] == "5"
    assert data["role"] == "regular_user"


def test_authenticate_wrong_password():
    service, user_repo = make_service()
    user_repo.get_by_username.return_value = bob()
    assert service.authenticate_user("bob", "wrongpass") is None


def test_authenticate_unknown_user():
    service, user_repo = make_service()
    assert service.authenticate_user("ghost", "bobpass") is None


def test_register_user():
    service, user_repo = make_service()
    new_user = service.register_user("carl", "carl@example.com", "secret1")
    assert new_user.username == "carl"
    assert new_user.role == "regular_user"
    assert new_user.password != "secret1"


def test_register_duplicate_username():
    service, user_repo = make_service()
    user_repo.get_by_username.return_value = bob()
    with pytest.raises(ConflictError):
        service.register_user("bob", "other@example.com", "secret1")
    user_repo.create.assert_not_called()


def test_register_duplicate_email():
    service, user_repo = make_service()
    user_repo.get_by_email.return_value = bob()
    with pytest.raises(ConflictError):
        service.register_user("newbie", "bob@example.com", "secret1")
    user_repo.create.assert_not_called()


def test_register_short_password():
    service, user_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.register_user("carl", "carl@example.com", "123")
    user_repo.create.assert_not_called()
