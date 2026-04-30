"""Transaction repository — Maria's rule-score query methods only.

Other query methods (payment lifecycle, anomaly model, general history) are
owned by other team members and must be added in their respective branches.
"""
import uuid
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import TransactionStatus
from app.models.transaction import Transaction


class TransactionRepository:

    # ------------------------------------------------------------------
    # Maria's rule-score query methods
    # ------------------------------------------------------------------

    @staticmethod
    def count_previous_transactions_to_receiver(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> int:
        """Count all transactions from sender to receiver, any status.

        Used by the new-beneficiary rule: 0 means the receiver is brand-new
        to this sender, which raises the risk score.
        """
        result = db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.sender_id == sender_id)
            .where(Transaction.receiver_id == receiver_id)
        )
        return result or 0

    @staticmethod
    def get_sender_average_transaction_amount(
        db: Session,
        sender_id: uuid.UUID,
    ) -> Decimal:
        """Return the average amount of APPROVED transactions sent by this sender.

        Used to determine whether the current amount is unusually large relative
        to the sender's normal behaviour. Returns Decimal('0') if no history exists.
        """
        result = db.scalar(
            select(func.avg(Transaction.amount))
            .where(Transaction.sender_id == sender_id)
            .where(Transaction.status == TransactionStatus.APPROVED)
        )
        return Decimal(str(result)) if result is not None else Decimal("0")

    @staticmethod
    def count_small_transactions_to_receiver(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        threshold: Decimal,
    ) -> int:
        """Count APPROVED transactions from sender to receiver below the given amount threshold.

        Used by the gradual trust-building rule to detect a pattern of small
        transactions before a large one.
        """
        result = db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.sender_id == sender_id)
            .where(Transaction.receiver_id == receiver_id)
            .where(Transaction.status == TransactionStatus.APPROVED)
            .where(Transaction.amount < threshold)
        )
        return result or 0

    @staticmethod
    def get_directly_approved_transactions_between_accounts(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> list[Transaction]:
        """Return all APPROVED transactions in either direction between two accounts.

        Used alongside count_approved_transactions_between_accounts in the contact
        repository to verify bidirectional trust history.
        """
        rows = db.scalars(
            select(Transaction)
            .where(Transaction.status == TransactionStatus.APPROVED)
            .where(
                or_(
                    (Transaction.sender_id == sender_id)
                    & (Transaction.receiver_id == receiver_id),
                    (Transaction.sender_id == receiver_id)
                    & (Transaction.receiver_id == sender_id),
                )
            )
            .order_by(Transaction.created_at)
        )
        return list(rows)

    @staticmethod
    def get_previous_approved_transactions_to_receiver(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> list[Transaction]:
        """Return APPROVED transactions from sender to receiver only (one direction).

        Used by the rule-score engine to inspect the directional payment history
        between sender and receiver when evaluating trust signals.
        """
        rows = db.scalars(
            select(Transaction)
            .where(Transaction.sender_id == sender_id)
            .where(Transaction.receiver_id == receiver_id)
            .where(Transaction.status == TransactionStatus.APPROVED)
            .order_by(Transaction.created_at)
        )
        return list(rows)
