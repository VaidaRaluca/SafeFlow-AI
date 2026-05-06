from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str
