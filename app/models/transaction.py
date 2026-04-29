import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CurrencyCode, TransactionStatus

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.risk_assessment import RiskAssessment


currency_code_enum = ENUM(
    CurrencyCode,
    name="currency_code",
    schema="public",
    create_type=False,
)

transaction_status_enum = ENUM(
    TransactionStatus,
    name="transaction_status",
    schema="public",
    create_type=False,
)


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint("sender_id <> receiver_id", name="transactions_no_self_transfer"),
        CheckConstraint("amount > 0", name="transactions_positive_amount"),
        CheckConstraint(
            "confirmed_at IS NULL OR confirmed_at >= created_at",
            name="transactions_confirmed_after_created",
        ),
        CheckConstraint(
            "settled_at IS NULL OR settled_at >= created_at",
            name="transactions_settled_after_created",
        ),
        CheckConstraint(
            "confirmed_at IS NULL OR settled_at IS NULL OR confirmed_at = settled_at",
            name="transactions_confirmed_equals_settled",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False,
    )

    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    currency: Mapped[CurrencyCode] = mapped_column(
        currency_code_enum,
        nullable=False,
        server_default=text("'EUR'::public.currency_code"),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[TransactionStatus] = mapped_column(
        transaction_status_enum,
        nullable=False,
        server_default=text("'PENDING'::public.transaction_status"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    requires_password_confirmation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    sender: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[sender_id],
        back_populates="sent_transactions",
    )

    receiver: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[receiver_id],
        back_populates="received_transactions",
    )

    risk_assessment: Mapped["RiskAssessment | None"] = relationship(
        "RiskAssessment",
        back_populates="transaction",
        uselist=False,
    )