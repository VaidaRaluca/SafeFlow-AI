"""Defines risk assessment orchestration ownership for backend skeleton only."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import RiskDecision, RiskLevel
from app.services.rule_score_service import RuleScoreService


LOW_RISK_THRESHOLD = Decimal("0.40")
HIGH_RISK_THRESHOLD = Decimal("0.70")


class RiskService:
    @staticmethod
    def evaluate_transaction_risk(
        db: Session,
        transaction_id: uuid.UUID,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        amount: Decimal,
        description: str | None,
        created_at: datetime,
    ) -> dict[str, Any]:
        rule_score, reason_codes = RuleScoreService.calculate_rule_score(
            db=db,
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            description=description,
            created_at=created_at,
        )

        anomaly_score = Decimal("0.00")
        combined_score = rule_score + anomaly_score

        risk_level, decision = RiskService._map_score_to_outcome(combined_score)

        return {
            "transaction_id": transaction_id,
            "rule_score": rule_score,
            "anomaly_score": anomaly_score,
            "combined_score": combined_score,
            "risk_level": risk_level,
            "decision": decision,
            "reason_codes": reason_codes,
            "evaluated_at": datetime.now(timezone.utc),
        }

    @staticmethod
    def _map_score_to_outcome(
        combined_score: Decimal,
    ) -> tuple[RiskLevel, RiskDecision]:
        if combined_score >= HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH, RiskDecision.REJECT

        if combined_score >= LOW_RISK_THRESHOLD:
            return RiskLevel.MEDIUM, RiskDecision.WARN

        return RiskLevel.LOW, RiskDecision.ALLOW
