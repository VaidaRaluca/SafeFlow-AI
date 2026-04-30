from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.account_repository import AccountRepository


class AccountService:
    def __init__(self, db: Session):
        self.account_repository = AccountRepository(db)

    def get_current_account(self, user_id: UUID) -> Account:
        account = self.account_repository.get_account_by_user_id(user_id)

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found for current user.",
            )

        return account
