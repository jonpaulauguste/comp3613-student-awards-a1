from typing import Optional

from app.repositories.user import UserRepository
from app.schemas.user import RegularUserCreate
from app.services.errors import ConflictError, InvalidInputError
from app.utilities.security import create_access_token, encrypt_password, verify_password

MIN_PASSWORD_LENGTH = 6


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(plaintext_password=password, encrypted_password=user.password):
            return None
        return create_access_token(data={"sub": f"{user.id}", "role": user.role})

    def register_user(self, username: str, email: str, password: str):
        username = (username or "").strip()
        email = (email or "").strip()
        if not username:
            raise InvalidInputError("Username is required.")
        if len(password or "") < MIN_PASSWORD_LENGTH:
            raise InvalidInputError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
            )
        if self.user_repo.get_by_username(username):
            raise ConflictError("Username is already taken.")
        if self.user_repo.get_by_email(email):
            raise ConflictError("Email is already registered.")
        new_user = RegularUserCreate(
            username=username,
            email=email,
            password=encrypt_password(password),
        )
        return self.user_repo.create(new_user)
