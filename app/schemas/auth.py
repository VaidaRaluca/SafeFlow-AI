from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel): # Data sent when a user logs in: email and password
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel): # JWT token returned after login so the frontend can authenticate future requests.
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RegisterResponse(BaseModel): # Returned after registration, usually containing the created user and token.
    user: UserResponse
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"