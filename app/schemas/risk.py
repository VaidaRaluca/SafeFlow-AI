import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import RiskDecision, RiskLevel


class RiskAssessmentResponse(BaseModel): # Sends rule score, anomaly score, combined score, risk level, and decision
    id: uuid.UUID
    transaction_id: uuid.UUID

    rule_score: Decimal = Field(
        ge=0,
        le=1,
        max_digits=4,
        decimal_places=3,
    )
    anomaly_score: Decimal = Field(
        ge=0,
        le=1,
        max_digits=4,
        decimal_places=3,
    )
    combined_score: Decimal = Field(
        ge=0,
        le=2,
        max_digits=4,
        decimal_places=3,
    )

    risk_level: RiskLevel
    decision: RiskDecision
    evaluated_at: datetime

    model_config = {
        "from_attributes": True,
    }
