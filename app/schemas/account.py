import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import CurrencyCode


class AccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    iban: str = Field(min_length=15, max_length=34)
    balance: Decimal
    currency: CurrencyCode
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
