from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.enums import CurrencyCode


class AccountBalanceError(Exception):
    """Base error for Andrei-owned settlement balance updates."""


class AccountNotFoundError(AccountBalanceError):
    """Raised when settlement cannot find one of the accounts."""


class InsufficientFundsError(AccountBalanceError):
    """Raised when settlement would make the sender balance negative."""


def decrease_balance(db: Session, account_id: UUID, amount: Decimal) -> Account:
    account = db.scalar(
        select(Account)
        .where(Account.id == account_id)
        .with_for_update()
    )

    if account is None:
        raise AccountNotFoundError("Sender account was not found.")

    if account.balance < amount:
        raise InsufficientFundsError("Insufficient funds for settlement.")

    account.balance -= amount
    db.flush()
    db.refresh(account)
    return account


def increase_balance(db: Session, account_id: UUID, amount: Decimal) -> Account:
    account = db.scalar(
        select(Account)
        .where(Account.id == account_id)
        .with_for_update()
    )

    if account is None:
        raise AccountNotFoundError("Receiver account was not found.")

    account.balance += amount
    db.flush()
    db.refresh(account)
    return account


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_account(
        self,
        user_id: UUID,
        iban: str,
        balance: Decimal = Decimal("0.00"),
        currency: CurrencyCode = CurrencyCode.EUR,
    ) -> Account:
        existing_account = self.get_account_by_user_id(user_id)
        if existing_account is not None:
            raise ValueError("User already has an account.")

        account = Account(
            user_id=user_id,
            iban=iban.upper(),
            balance=balance,
            currency=currency,
        )

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def get_account_by_id(self, account_id: UUID) -> Account | None:
        stmt = select(Account).where(Account.id == account_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_account_by_user_id(self, user_id: UUID) -> Account | None:
        stmt = select(Account).where(Account.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_account_by_iban(self, iban: str) -> Account | None:
        stmt = select(Account).where(Account.iban == iban.upper())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_account_balance(self, account_id: UUID) -> Decimal | None:
        stmt = select(Account.balance).where(Account.id == account_id)
        return self.db.execute(stmt).scalar_one_or_none()
