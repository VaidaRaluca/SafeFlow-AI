from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import ACCESS_TOKEN_TYPE, TokenError, decode_token
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
        user_id = UUID(str(payload.get("sub")))
    except (TokenError, ValueError) as exc:
        raise credentials_exception from exc

    user = UserRepository(db).get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user
