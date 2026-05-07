import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.enums import TransactionStatus
from app.models.transaction import Transaction


SAFE_CONTACT_STATUSES: tuple[TransactionStatus, ...] = (
    TransactionStatus.APPROVED,
    TransactionStatus.SETTLED,
)


class ContactRepository:

    @staticmethod
    def get_contact(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> bool:
        """Return True when a contact row exists for (sender_id, receiver_id)."""
        return db.scalar(
            select(Contact.id)
            .where(Contact.sender_id == sender_id)
            .where(Contact.receiver_id == receiver_id)
        ) is not None

    @staticmethod
    def _get_contact_model(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> Contact | None:
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
    ) -> bool:
        """Insert a new contact row with is_trusted=False. Caller owns the commit."""
        existing_contact = ContactRepository._get_contact_model(db, sender_id, receiver_id)
        if existing_contact is not None:
            return False

        contact = Contact(
            sender_id=sender_id,
            receiver_id=receiver_id,
            is_trusted=False,
        )
        db.add(contact)
        db.flush()
        return True

    @staticmethod
    def is_receiver_trusted(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> bool:
        """Return True if the contact exists and is marked trusted, otherwise False."""
        contact = ContactRepository._get_contact_model(db, sender_id, receiver_id)
        if contact is None:
            return False
        return contact.is_trusted

    @staticmethod
    def update_trusted_status(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        trusted: bool,
    ) -> bool:
        """Set is_trusted on the contact row. Returns False if it does not exist."""
        contact = ContactRepository._get_contact_model(db, sender_id, receiver_id)
        if contact is None:
            return False
        contact.is_trusted = trusted
        db.flush()
        return True

    @staticmethod
    def count_approved_transactions_between_accounts(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> int:
        """Count safe APPROVED/SETTLED transactions between these accounts.

        Used to determine whether the pair has enough safe history to mark the
        beneficiary trusted.
        """
        result = db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.status.in_(SAFE_CONTACT_STATUSES))
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
