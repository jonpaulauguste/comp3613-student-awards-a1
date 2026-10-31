"""Unit tests: password hashing and tokens (no database)."""

import jwt

from app.config import get_settings
from app.utilities.security import create_access_token, encrypt_password, verify_password


def test_password_hash():
    hashed = encrypt_password("mypass")
    assert hashed != "mypass"


def test_check_password():
    hashed = encrypt_password("mypass")
    assert verify_password("mypass", hashed) is True
    assert verify_password("wrongpass", hashed) is False


def test_access_token():
    token = create_access_token({"sub": "9", "role": "admin"})
    settings = get_settings()
    data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    assert data["sub"] == "9"
    assert data["role"] == "admin"
    assert "exp" in data
