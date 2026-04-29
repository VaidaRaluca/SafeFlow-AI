import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import CurrencyCode, TransactionStatus
from app.schemas.risk import RiskAssessmentResponse


class TransactionResponse(BaseModel): # Sends basic transaction data for transaction history lists.
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
        "from_attributes": True
    }


class TransactionDetailResponse(TransactionResponse): # Sends full transaction data, including risk assessment details.
    risk_assessment: RiskAssessmentResponse | None = None


class TransactionListResponse(BaseModel): # Wraps multiple transactions into one response for /api/transactions/me
    transactions: list[TransactionResponse]