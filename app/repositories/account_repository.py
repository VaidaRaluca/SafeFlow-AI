from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.enums import CurrencyCode
from app.schemas.account import AccountResponse


class AccountBalanceError(Exception):
    """Base error for Andrei-owned settlement balance updates."""


class AccountNotFoundError(AccountBalanceError):
    """Raised when settlement cannot find one of the accounts."""


class InsufficientFundsError(AccountBalanceError):
    """Raised when settlement would make the sender balance negative."""


def _to_account_response(account: Account) -> AccountResponse:
    return AccountResponse.model_validate(account)


def decrease_balance(db: Session, account_id: UUID, amount: Decimal) -> AccountResponse:
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
    return _to_account_response(account)


def increase_balance(db: Session, account_id: UUID, amount: Decimal) -> AccountResponse:
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
    return _to_account_response(account)


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_account(
        self,
        user_id: UUID,
        iban: str,
        balance: Decimal = Decimal("0.00"),
        currency: CurrencyCode = CurrencyCode.EUR,
    ) -> AccountResponse:
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

        return _to_account_response(account)

    def get_account_by_id(self, account_id: UUID) -> AccountResponse | None:
        stmt = select(Account).where(Account.id == account_id)
        account = self.db.execute(stmt).scalar_one_or_none()
        if account is None:
            return None
        return _to_account_response(account)

    def get_account_by_user_id(self, user_id: UUID) -> AccountResponse | None:
        stmt = select(Account).where(Account.user_id == user_id)
        account = self.db.execute(stmt).scalar_one_or_none()
        if account is None:
            return None
        return _to_account_response(account)

    def get_account_by_iban(self, iban: str) -> AccountResponse | None:
        stmt = select(Account).where(Account.iban == iban.upper())
        account = self.db.execute(stmt).scalar_one_or_none()
        if account is None:
            return None
        return _to_account_response(account)

    def get_account_balance(self, account_id: UUID) -> Decimal | None:
        stmt = select(Account.balance).where(Account.id == account_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def decrease_balance(self, account_id: UUID, amount: Decimal) -> AccountResponse:
        return decrease_balance(self.db, account_id, amount)

    def increase_balance(self, account_id: UUID, amount: Decimal) -> AccountResponse:
        return increase_balance(self.db, account_id, amount)
