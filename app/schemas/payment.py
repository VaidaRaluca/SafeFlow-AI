import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.core.enums import CurrencyCode


class PaymentCreate(BaseModel): # Payment form data sent by the sender: receiver, amount, currency, and description.
    receiver_id: uuid.UUID | None = Field(
        default=None,
    )
    receiver_iban: str | None = Field(
        default=None,
        min_length=15,
        max_length=34,
    )
    amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2,
    )
    currency: CurrencyCode = CurrencyCode.EUR
    description: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_receiver(self):
        if self.receiver_id is None and self.receiver_iban is None:
            raise ValueError("Either receiver_id or receiver_iban is required.")

        return self


class PaymentConfirm(BaseModel): # Sent when the user confirms a payment, optionally with password for warned transactions.
    password: str | None = None


class PaymentCancel(BaseModel): # Sent when the user cancels a payment, optionally with a cancellation reason.
    reason: str | None = Field(default=None, max_length=500)
