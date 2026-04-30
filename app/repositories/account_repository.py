import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account


class AccountBalanceError(Exception):
    """Base error for Andrei-owned settlement balance updates."""


class AccountNotFoundError(AccountBalanceError):
    """Raised when settlement cannot find one of the accounts."""


class InsufficientFundsError(AccountBalanceError):
    """Raised when settlement would make the sender balance negative."""


def decrease_balance(db: Session, account_id: uuid.UUID, amount: Decimal) -> Account:
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


def increase_balance(db: Session, account_id: uuid.UUID, amount: Decimal) -> Account:
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
