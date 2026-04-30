from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterResponse, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register(self, payload: UserCreate) -> RegisterResponse:
        if self.user_repository.user_exists_by_email(str(payload.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = self.user_repository.create_user(
            full_name=payload.full_name,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
        )

        return RegisterResponse(
            user=user,
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.user_repository.get_user_by_email(str(payload.email))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self._tokens_for_user(str(user.id))

    def logout(self) -> dict[str, str]:
        return {"message": "Logged out successfully."}

    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            token_payload = decode_token(payload.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
            user_id = UUID(str(token_payload.get("sub")))
        except (TokenError, ValueError) as exc:
            raise credentials_exception from exc

        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception

        return self._tokens_for_user(str(user.id))

    def _tokens_for_user(self, user_id: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
