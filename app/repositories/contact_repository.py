import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.enums import TransactionStatus
from app.models.transaction import Transaction


class ContactRepository:

    @staticmethod
    def get_contact(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> Contact | None:
        """Return the contact row for (sender_id, receiver_id), or None if not found."""
        return db.scalar(
            select(Contact)
            .where(Contact.sender_id == sender_id)
            .where(Contact.receiver_id == receiver_id)
        )

    @staticmethod
    def create_contact(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> Contact:
        """Insert a new contact row with is_trusted=False. Caller owns the commit."""
        contact = Contact(
            sender_id=sender_id,
            receiver_id=receiver_id,
            is_trusted=False,
        )
        db.add(contact)
        db.flush()
        return contact

    @staticmethod
    def is_receiver_trusted(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> bool:
        """Return True if the contact exists and is marked trusted, otherwise False."""
        contact = ContactRepository.get_contact(db, sender_id, receiver_id)
        if contact is None:
            return False
        return contact.is_trusted

    @staticmethod
    def update_trusted_status(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        trusted: bool,
    ) -> Contact | None:
        """Set is_trusted on the contact row. Returns None if the contact does not exist."""
        contact = ContactRepository.get_contact(db, sender_id, receiver_id)
        if contact is None:
            return None
        contact.is_trusted = trusted
        db.flush()
        return contact

    @staticmethod
    def count_approved_transactions_between_accounts(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> int:
        """Count APPROVED transactions in either direction between these two accounts.

        Used by the gradual trust-building rule to determine whether the pair
        has enough approved history to justify lowering the risk score.
        """
        result = db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.status == TransactionStatus.APPROVED)
            .where(
                or_(
                    (Transaction.sender_id == sender_id)
                    & (Transaction.receiver_id == receiver_id),
                    (Transaction.sender_id == receiver_id)
                    & (Transaction.receiver_id == sender_id),
                )
            )
        )
        return result or 0
