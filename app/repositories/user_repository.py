from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserResponse


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        full_name: str,
        email: str,
        password_hash: str,
    ) -> UserResponse:
        user = User(
            full_name=full_name,
            email=email.lower(),
            password_hash=password_hash,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserResponse.model_validate(user)

    def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        stmt = select(User).where(User.id == user_id)
        user = self.db.execute(stmt).scalar_one_or_none()
        if user is None:
            return None
        return UserResponse.model_validate(user)

    def get_user_by_email(self, email: str) -> UserResponse | None:
        stmt = select(User).where(User.email == email.lower())
        user = self.db.execute(stmt).scalar_one_or_none()
        if user is None:
            return None
        return UserResponse.model_validate(user)

    def user_exists_by_email(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email.lower())
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def get_password_hash_by_email(self, email: str) -> str | None:
        stmt = select(User.password_hash).where(User.email == email.lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_password_hash_by_id(self, user_id: UUID) -> str | None:
        stmt = select(User.password_hash).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
