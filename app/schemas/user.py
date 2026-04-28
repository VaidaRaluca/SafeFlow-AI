import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel): # Data sent when a user registers: full name, email, and plain password.
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel): # Safe user data returned to the frontend, without password_hash
    id: uuid.UUID
    full_name: str
    email: EmailStr
    created_at: datetime

    model_config = {
        "from_attributes": True
    }