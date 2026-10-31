from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError

from app.config import get_settings
from app.dependencies.session import SessionDep
from app.models.user import User
from app.repositories.user import UserRepository


def _token_from_request(request: Request) -> Optional[str]:
    """Read the JWT from an ``Authorization: Bearer`` header, else the cookie.

    The header lets API clients (Postman, mobile) authenticate; the cookie keeps
    the server-rendered pages working.
    """
    header = request.headers.get("Authorization", "")
    scheme, _, credentials = header.partition(" ")
    if scheme.lower() == "bearer" and credentials.strip():
        return credentials.strip()
    return request.cookies.get("access_token")


async def get_current_user(request: Request, db: SessionDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _token_from_request(request)
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[get_settings().jwt_algorithm],
        )
        user_id = int(payload.get("sub"))
    except (InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def is_logged_in(request: Request, db: SessionDep):
    try:
        await get_current_user(request, db)
        return True
    except Exception:
        return False


IsUserLoggedIn = Annotated[bool, Depends(is_logged_in)]
AuthDep = Annotated[User, Depends(get_current_user)]


async def is_admin(user: User):
    return user.role == "admin"


async def is_admin_dep(user: AuthDep):
    # Logged in but wrong role is 403 Forbidden, not 401 Unauthorized.
    if not await is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def is_student_dep(user: AuthDep):
    if await is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required",
        )
    return user


AdminDep = Annotated[User, Depends(is_admin_dep)]
StudentDep = Annotated[User, Depends(is_student_dep)]
