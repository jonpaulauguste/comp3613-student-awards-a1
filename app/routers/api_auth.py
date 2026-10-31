from fastapi import HTTPException, status

from app.dependencies import AdminDep, AuthDep, SessionDep
from app.repositories.user import UserRepository
from app.schemas.api import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from . import api_router


@api_router.post("/auth/login", response_model=TokenResponse)
async def api_login(credentials: LoginRequest, db: SessionDep):
    token = AuthService(UserRepository(db)).authenticate_user(
        credentials.username, credentials.password
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=token)


@api_router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def api_register(payload: RegisterRequest, db: SessionDep):
    return AuthService(UserRepository(db)).register_user(
        payload.username, payload.email, payload.password
    )


@api_router.get("/users/me", response_model=UserResponse)
async def api_current_user(user: AuthDep):
    return user


@api_router.get("/users", response_model=list[UserResponse])
async def api_list_users(admin: AdminDep, db: SessionDep):
    return UserService(UserRepository(db)).get_all_users()
