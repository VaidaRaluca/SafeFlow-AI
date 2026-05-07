"""Transaction query-only data-access methods."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.enums import CurrencyCode, TransactionStatus
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionDetailResponse, TransactionResponse


SAFE_TRANSACTION_STATUSES: tuple[TransactionStatus, ...] = (
    TransactionStatus.APPROVED,
    TransactionStatus.SETTLED,
)


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # Fetch a single transaction by its unique ID
    def get_transaction_by_id(self, transaction_id: uuid.UUID) -> TransactionResponse | None:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        transaction = self.db.scalar(stmt)
        if transaction is None:
            return None
        return _to_transaction_response(transaction)

    # Retrieve all transactions where the account is either sender or receiver
    def get_transactions_for_account(self, account_id: uuid.UUID) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(
                or_(
                    Transaction.sender_id == account_id,
                    Transaction.receiver_id == account_id,
                )
            )
            .order_by(Transaction.created_at.desc())
        )
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Fetch full transaction details including related entities
    def get_transaction_details(self, transaction_id: uuid.UUID) -> TransactionDetailResponse | None:
        stmt = (
            select(Transaction)
            .options(
                joinedload(Transaction.sender),
                joinedload(Transaction.receiver),
                joinedload(Transaction.risk_assessment),
            )
            .where(Transaction.id == transaction_id)
        )
        transaction = self.db.scalar(stmt)
        if transaction is None:
            return None
        return _to_transaction_detail_response(transaction)

    # Get all transactions where the given account is the sender
    def get_transactions_by_sender(self, sender_account_id: uuid.UUID) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(Transaction.sender_id == sender_account_id)
            .order_by(Transaction.created_at.desc())
        )
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Get all transactions where the given account is the receiver
    def get_transactions_by_receiver(self, receiver_account_id: uuid.UUID) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(Transaction.receiver_id == receiver_account_id)
            .order_by(Transaction.created_at.desc())
        )
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Retrieve transaction history between a specific sender and receiver
    def get_transactions_between_accounts(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
    ) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.sender_id == sender_account_id,
                Transaction.receiver_id == receiver_account_id,
            )
            .order_by(Transaction.created_at.desc())
        )
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Fetch the most recent transactions for a given account (used in dashboard/history)
    def get_recent_transactions_for_account(
        self,
        account_id: uuid.UUID,
        limit: int = 10,
    ) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(
                or_(
                    Transaction.sender_id == account_id,
                    Transaction.receiver_id == account_id,
                )
            )
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Retrieve only safe (approved/settled) transactions for model training
    def get_safe_sender_history_for_training(
        self,
        sender_account_id: uuid.UUID,
    ) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.sender_id == sender_account_id,
                Transaction.status.in_(SAFE_TRANSACTION_STATUSES),
            )
            .order_by(Transaction.created_at.desc())
        )
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Compute aggregate statistics (count, avg, min, max, sum) for sender transactions
    def get_sender_transaction_statistics(
        self,
        sender_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> dict[str, Any]:
        stmt = select(
            func.count(Transaction.id),
            func.avg(Transaction.amount),
            func.min(Transaction.amount),
            func.max(Transaction.amount),
            func.sum(Transaction.amount),
        ).where(Transaction.sender_id == sender_account_id)
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        if safe_only:
            stmt = stmt.where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))

        count, avg_amount, min_amount, max_amount, total_amount = self.db.execute(stmt).one()
        return {
            "count": int(count or 0),
            "avg_amount": avg_amount,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "total_amount": total_amount,
        }

    # Calculate the median transaction amount for a sender (with fallback if DB doesn't support it)
    def get_sender_median_transaction_amount(
        self,
        sender_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> Decimal | None:
        try:
            stmt = select(
                func.percentile_cont(0.5).within_group(Transaction.amount)
            ).where(Transaction.sender_id == sender_account_id)
            stmt = _exclude_transaction(stmt, exclude_transaction_id)
            if safe_only:
                stmt = stmt.where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))
            median_value = self.db.scalar(stmt)
            return median_value
        except SQLAlchemyError:
            self.db.rollback()
            amounts_stmt = (
                select(Transaction.amount)
                .where(Transaction.sender_id == sender_account_id)
                .order_by(Transaction.amount.asc())
            )
            amounts_stmt = _exclude_transaction(amounts_stmt, exclude_transaction_id)
            if safe_only:
                amounts_stmt = amounts_stmt.where(
                    Transaction.status.in_(SAFE_TRANSACTION_STATUSES)
                )
            amounts = list(self.db.scalars(amounts_stmt).all())
            if not amounts:
                return None

            size = len(amounts)
            middle = size // 2
            if size % 2 == 1:
                return amounts[middle]

            return (amounts[middle - 1] + amounts[middle]) / Decimal("2")

    # Fetch historical transactions from sender to receiver for feature engineering
    def get_receiver_history_for_features(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.sender_id == sender_account_id,
                Transaction.receiver_id == receiver_account_id,
            )
            .order_by(Transaction.created_at.desc())
        )
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        if safe_only:
            stmt = stmt.where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    # Count how many previous transactions exist between sender and receiver
    def get_previous_transactions_to_receiver_for_features(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> int:
        stmt = select(func.count(Transaction.id)).where(
            Transaction.sender_id == sender_account_id,
            Transaction.receiver_id == receiver_account_id,
        )
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        if safe_only:
            stmt = stmt.where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))
        return int(self.db.scalar(stmt) or 0)

    # Compute number of days since the last transaction to a specific receiver
    def get_days_since_last_transaction_to_receiver(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> int | None:
        stmt = select(func.max(Transaction.created_at)).where(
            Transaction.sender_id == sender_account_id,
            Transaction.receiver_id == receiver_account_id,
        )
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        if safe_only:
            stmt = stmt.where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))
        last_transaction_at = self.db.scalar(stmt)
        if last_transaction_at is None:
            return None

        if last_transaction_at.tzinfo is None:
            last_transaction_at = last_transaction_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        return (now - last_transaction_at).days

    # Count transactions below a threshold amount for gradual pattern detection
    def get_small_transaction_count_to_receiver_for_features(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        threshold: Decimal = Decimal("100.00"),
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> int:
        stmt = select(func.count(Transaction.id)).where(
            Transaction.sender_id == sender_account_id,
            Transaction.receiver_id == receiver_account_id,
            Transaction.amount < threshold,
        )
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        if safe_only:
            stmt = stmt.where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))
        return int(self.db.scalar(stmt) or 0)

    # Count safe transactions (approved/settled) for a sender
    def get_sender_safe_transaction_count(
        self,
        sender_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
    ) -> int:
        stmt = select(func.count(Transaction.id)).where(
            Transaction.sender_id == sender_account_id,
            Transaction.status.in_(SAFE_TRANSACTION_STATUSES),
        )
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        return int(self.db.scalar(stmt) or 0)

    
    # Fetch all safe transactions across all users for global Isolation Forest training.
    def get_all_safe_transactions_for_training(self) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(Transaction.status.in_(SAFE_TRANSACTION_STATUSES))
            .order_by(Transaction.created_at.desc())
        )

        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    def count_previous_transactions_to_receiver(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> int:
        return self.get_previous_transactions_to_receiver_for_features(
            sender_account_id=sender_account_id,
            receiver_account_id=receiver_account_id,
            exclude_transaction_id=exclude_transaction_id,
            safe_only=safe_only,
        )

    def get_sender_average_transaction_amount(
        self,
        sender_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> Decimal:
        statistics = self.get_sender_transaction_statistics(
            sender_account_id=sender_account_id,
            exclude_transaction_id=exclude_transaction_id,
            safe_only=safe_only,
        )
        return statistics["avg_amount"] or Decimal("0.00")

    def count_small_transactions_to_receiver(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        threshold: Decimal = Decimal("100.00"),
        exclude_transaction_id: uuid.UUID | None = None,
        safe_only: bool = True,
    ) -> int:
        return self.get_small_transaction_count_to_receiver_for_features(
            sender_account_id=sender_account_id,
            receiver_account_id=receiver_account_id,
            threshold=threshold,
            exclude_transaction_id=exclude_transaction_id,
            safe_only=safe_only,
        )

    def get_directly_approved_transactions_between_accounts(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
    ) -> list[TransactionResponse]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.sender_id == sender_account_id,
                Transaction.receiver_id == receiver_account_id,
                Transaction.status.in_(SAFE_TRANSACTION_STATUSES),
            )
            .order_by(Transaction.created_at.desc())
        )
        stmt = _exclude_transaction(stmt, exclude_transaction_id)
        return [_to_transaction_response(transaction) for transaction in self.db.scalars(stmt).all()]

    def get_previous_approved_transactions_to_receiver(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        exclude_transaction_id: uuid.UUID | None = None,
    ) -> list[TransactionResponse]:
        return self.get_directly_approved_transactions_between_accounts(
            sender_account_id=sender_account_id,
            receiver_account_id=receiver_account_id,
            exclude_transaction_id=exclude_transaction_id,
        )


def _exclude_transaction(stmt, transaction_id: uuid.UUID | None):
    if transaction_id is None:
        return stmt

    return stmt.where(Transaction.id != transaction_id)


def _to_transaction_response(
    transaction: Transaction,
) -> TransactionResponse:
    return TransactionResponse.model_validate(transaction)


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
