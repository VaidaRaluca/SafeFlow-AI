import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RiskDecision, RiskLevel

if TYPE_CHECKING:
    from app.models.transaction import Transaction


risk_level_enum = ENUM(
    RiskLevel,
    name="risk_level",
    schema="public",
    create_type=False,
)

risk_decision_enum = ENUM(
    RiskDecision,
    name="risk_decision",
    schema="public",
    create_type=False,
)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    __table_args__ = (
        CheckConstraint(
            "rule_score >= 0 AND rule_score <= 1",
            name="risk_rule_score_range",
        ),
        CheckConstraint(
            "anomaly_score >= 0 AND anomaly_score <= 1",
            name="risk_anomaly_score_range",
        ),
        CheckConstraint(
            "combined_score >= 0 AND combined_score <= 2",
            name="risk_combined_score_range",
        ),
        CheckConstraint(
            """
            (
                risk_level = 'LOW' AND decision = 'ALLOW'
            )
            OR (
                risk_level = 'MEDIUM' AND decision = 'WARN'
            )
            OR (
                risk_level = 'HIGH' AND decision = 'REJECT'
            )
            """,
            name="risk_level_decision_consistency",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        nullable=False,
        unique=True,
    )

    rule_score: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        nullable=False,
    )

    anomaly_score: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        nullable=False,
    )

    combined_score: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        nullable=False,
    )

    risk_level: Mapped[RiskLevel] = mapped_column(
        risk_level_enum,
        nullable=False,
    )

    decision: Mapped[RiskDecision] = mapped_column(
        risk_decision_enum,
        nullable=False,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    transaction: Mapped["Transaction"] = relationship(
        "Transaction",
        back_populates="risk_assessment",
    )