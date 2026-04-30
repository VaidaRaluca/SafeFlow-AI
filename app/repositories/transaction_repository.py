import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import CurrencyCode, TransactionStatus
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionDetailResponse


def _to_transaction_detail_response(
    transaction: Transaction,
) -> TransactionDetailResponse:
    return TransactionDetailResponse.model_validate(transaction)


def _get_transaction_for_update(
    db: Session,
    transaction_id: uuid.UUID,
) -> Transaction | None:
    return db.scalar(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .with_for_update()
    )


def create_pending_transaction(
    db: Session,
    sender_id: uuid.UUID,
    receiver_id: uuid.UUID,
    amount: Decimal,
    currency: CurrencyCode,
    description: str | None = None,
) -> TransactionDetailResponse:
    transaction = Transaction(
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        currency=currency,
        description=description,
        status=TransactionStatus.PENDING,
        requires_password_confirmation=False,
    )

    db.add(transaction)
    db.flush()
    db.refresh(transaction)
    return _to_transaction_detail_response(transaction)


def get_transaction_for_update(
    db: Session,
    transaction_id: uuid.UUID,
) -> TransactionDetailResponse | None:
    transaction = _get_transaction_for_update(db, transaction_id)

    if transaction is None:
        return None

    return _to_transaction_detail_response(transaction)


def update_transaction_status(
    db: Session,
    transaction_id: uuid.UUID,
    status: TransactionStatus,
) -> TransactionDetailResponse | None:
    transaction = _get_transaction_for_update(db, transaction_id)

    if transaction is None:
        return None

    transaction.status = status
    db.flush()
    db.refresh(transaction)
    return _to_transaction_detail_response(transaction)


def mark_transaction_as_approved(
    db: Session,
    transaction_id: uuid.UUID,
) -> TransactionDetailResponse | None:
    return update_transaction_status(db, transaction_id, TransactionStatus.APPROVED)


def mark_transaction_as_warned(
    db: Session,
    transaction_id: uuid.UUID,
) -> TransactionDetailResponse | None:
    return update_transaction_status(db, transaction_id, TransactionStatus.WARNED)


def mark_transaction_as_rejected(
    db: Session,
    transaction_id: uuid.UUID,
) -> TransactionDetailResponse | None:
    return update_transaction_status(db, transaction_id, TransactionStatus.REJECTED)


def mark_transaction_as_settled(
    db: Session,
    transaction_id: uuid.UUID,
) -> TransactionDetailResponse | None:
    return update_transaction_status(db, transaction_id, TransactionStatus.SETTLED)


def mark_transaction_as_canceled(
    db: Session,
    transaction_id: uuid.UUID,
) -> TransactionDetailResponse | None:
    return update_transaction_status(db, transaction_id, TransactionStatus.CANCELED)


def set_requires_password_confirmation(
    db: Session,
    transaction_id: uuid.UUID,
    requires_password_confirmation: bool,
) -> TransactionDetailResponse | None:
    transaction = _get_transaction_for_update(db, transaction_id)

    if transaction is None:
        return None

    transaction.requires_password_confirmation = requires_password_confirmation
    db.flush()
    db.refresh(transaction)
    return _to_transaction_detail_response(transaction)


def set_confirmed_at(
    db: Session,
    transaction_id: uuid.UUID,
    confirmed_at: datetime,
) -> TransactionDetailResponse | None:
    transaction = _get_transaction_for_update(db, transaction_id)

    if transaction is None:
        return None

    transaction.confirmed_at = confirmed_at
    db.flush()
    db.refresh(transaction)
    return _to_transaction_detail_response(transaction)


def set_settled_at(
    db: Session,
    transaction_id: uuid.UUID,
    settled_at: datetime,
) -> TransactionDetailResponse | None:
    transaction = _get_transaction_for_update(db, transaction_id)

    if transaction is None:
        return None

    transaction.settled_at = settled_at
    db.flush()
    db.refresh(transaction)
    return _to_transaction_detail_response(transaction)
