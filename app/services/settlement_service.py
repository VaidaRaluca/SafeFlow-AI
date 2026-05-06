from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories import account_repository, transaction_repository
from app.schemas.transaction import TransactionDetailResponse


APPROVED_STATUS = "APPROVED"
WARNED_STATUS = "WARNED"
SETTLED_STATUS = "SETTLED"


class SettlementError(Exception):
    """Base error for Andrei-owned settlement orchestration."""


class SettlementInvalidStatusError(SettlementError):
    """Raised when a transaction cannot be settled from its current status."""


class SettlementAccountError(SettlementError):
    """Raised when account balance movement fails during settlement."""


def settle_transaction(
    db: Session,
    transaction: TransactionDetailResponse,
) -> TransactionDetailResponse:
    status = _enum_value(transaction.status)

    if status == SETTLED_STATUS:
        raise SettlementInvalidStatusError("Transaction is already settled.")

    if status not in {APPROVED_STATUS, WARNED_STATUS}:
        raise SettlementInvalidStatusError(
            "Only approved or warned transactions can be settled."
        )

    settled_at = datetime.now(timezone.utc)

    try:
        account_repository.decrease_balance(
            db=db,
            account_id=transaction.sender_id,
            amount=transaction.amount,
        )
        account_repository.increase_balance(
            db=db,
            account_id=transaction.receiver_id,
            amount=transaction.amount,
        )
    except account_repository.AccountBalanceError as exc:
        raise SettlementAccountError(str(exc)) from exc

    transaction_repository.set_confirmed_at(
        db=db,
        transaction_id=transaction.id,
        confirmed_at=settled_at,
    )
    transaction_repository.set_settled_at(
        db=db,
        transaction_id=transaction.id,
        settled_at=settled_at,
    )
    settled_transaction = transaction_repository.mark_transaction_as_settled(
        db=db,
        transaction_id=transaction.id,
    )

    if settled_transaction is None:
        raise SettlementInvalidStatusError("Transaction was not found.")

    return settled_transaction


def _enum_value(value: object) -> str:
    raw_value = getattr(value, "value", value)
    return str(raw_value).upper()
