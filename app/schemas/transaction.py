import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.core.enums import CurrencyCode, TransactionStatus
from app.schemas.risk import RiskAssessmentResponse


class TransactionResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    amount: Decimal
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


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
