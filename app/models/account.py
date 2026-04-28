import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CurrencyCode

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.contact import Contact
    from app.models.transaction import Transaction


currency_code_enum = ENUM(
    CurrencyCode,
    name="currency_code",
    schema="public",
    create_type=False,
)


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        CheckConstraint("balance >= 0", name="accounts_balance_non_negative"),
        CheckConstraint(
            "char_length(iban) >= 15 AND char_length(iban) <= 34",
            name="accounts_iban_length",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    iban: Mapped[str] = mapped_column(
        String(34),
        nullable=False,
        unique=True,
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0.00"),
    )

    currency: Mapped[CurrencyCode] = mapped_column(
        currency_code_enum,
        nullable=False,
        server_default=text("'EUR'::public.currency_code"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="accounts",
    )

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_id",
        back_populates="sender",
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="receiver",
    )

    sent_contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        foreign_keys="Contact.sender_id",
        back_populates="sender",
    )

    received_contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        foreign_keys="Contact.receiver_id",
        back_populates="receiver",
    )