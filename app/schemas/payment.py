import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import CurrencyCode


class PaymentCreate(BaseModel): # Payment form data sent by the sender: receiver, amount, currency, and description.
    receiver_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: CurrencyCode = CurrencyCode.EUR
    description: str | None = Field(default=None, max_length=500)


class PaymentConfirm(BaseModel): # Sent when the user confirms a payment, optionally with password for warned transactions.
    password: str | None = None


class PaymentCancel(BaseModel): # Sent when the user cancels a payment, optionally with a cancellation reason.
    reason: str | None = Field(default=None, max_length=500)