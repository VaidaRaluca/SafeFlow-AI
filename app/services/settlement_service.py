from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import account_repository, transaction_repository
from app.repositories.contact_repository import ContactRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionDetailResponse


APPROVED_STATUS = "APPROVED"
WARNED_STATUS = "WARNED"
SETTLED_STATUS = "SETTLED"
TRUSTED_SAFE_TRANSACTION_THRESHOLD = 5


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
    account_repo = account_repository.AccountRepository(db)

    try:
        account_repo.decrease_balance(
            account_id=transaction.sender_id,
            amount=transaction.amount,
        )
        account_repo.increase_balance(
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

    _update_contact_trust_after_settlement(
        db=db,
        sender_id=transaction.sender_id,
        receiver_id=transaction.receiver_id,
    )

    detailed_transaction = TransactionRepository(db).get_transaction_details(
        transaction.id,
    )

    if detailed_transaction is None:
        raise SettlementInvalidStatusError("Transaction was not found.")

    return detailed_transaction


def _update_contact_trust_after_settlement(
    db: Session,
    sender_id: UUID,
    receiver_id: UUID,
) -> None:
    safe_transaction_count = ContactRepository.count_approved_transactions_between_accounts(
        db=db,
        sender_id=sender_id,
        receiver_id=receiver_id,
    )

    if safe_transaction_count >= TRUSTED_SAFE_TRANSACTION_THRESHOLD:
        ContactRepository.update_trusted_status(
            db=db,
            sender_id=sender_id,
            receiver_id=receiver_id,
            trusted=True,
        )


def _enum_value(value: object) -> str:
    raw_value = getattr(value, "value", value)
    return str(raw_value).upper()
