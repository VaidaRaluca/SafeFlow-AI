import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import CurrencyCode, TransactionStatus
from app.schemas.risk import RiskAssessmentResponse


class TransactionResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    sender_iban: str | None = None
    sender_name: str | None = None
    receiver_iban: str | None = None
    receiver_name: str | None = None
    amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2,
    )
    currency: CurrencyCode
    description: str | None
    status: TransactionStatus
    created_at: datetime
    confirmed_at: datetime | None
    settled_at: datetime | None
    requires_password_confirmation: bool

    model_config = {
        "from_attributes": True,
    }


class TransactionDetailResponse(TransactionResponse):
    risk_assessment: RiskAssessmentResponse | None = None

    model_config = {
        "from_attributes": True,
    }


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
