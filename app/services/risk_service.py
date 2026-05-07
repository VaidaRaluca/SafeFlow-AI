"""Risk assessment orchestration for rule and anomaly scoring."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import RiskDecision, RiskLevel
from app.repositories.risk_assessment_repository import RiskAssessmentRepository
from app.schemas.risk import RiskAssessmentResponse
from app.services.rule_score_service import RuleScoreService


LOW_RISK_THRESHOLD = Decimal("0.40")
HIGH_RISK_THRESHOLD = Decimal("0.70")
RULE_SCORE_WEIGHT = Decimal("0.60")
ANOMALY_SCORE_WEIGHT = Decimal("0.40")
SCORE_QUANTIZER = Decimal("0.001")


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
    ) -> RiskAssessmentResponse:
        rule_score = RuleScoreService.calculate_rule_score(
            db=db,
            transaction_id=transaction_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            description=description,
            created_at=created_at,
        )

        anomaly_score = RiskService._calculate_anomaly_score(
            db=db,
            transaction_id=transaction_id,
        )
        combined_score = RiskService._calculate_combined_score(
            rule_score=rule_score,
            anomaly_score=anomaly_score,
        )

        risk_level, decision = RiskService._map_score_to_outcome(combined_score)

        return RiskAssessmentRepository(db).create_risk_assessment(
            transaction_id=transaction_id,
            rule_score=RiskService._quantize_score(rule_score),
            anomaly_score=RiskService._quantize_score(anomaly_score),
            combined_score=combined_score,
            risk_level=risk_level,
            decision=decision,
            evaluated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _calculate_anomaly_score(
        db: Session,
        transaction_id: uuid.UUID,
    ) -> Decimal:
        from app.services.anomaly_score_service import AnomalyScoreService

        anomaly_score = AnomalyScoreService(db).calculate_anomaly_score_for_transaction(
            transaction_id,
        )
        return RiskService._quantize_score(Decimal(str(anomaly_score)))

    @staticmethod
    def _calculate_combined_score(
        rule_score: Decimal,
        anomaly_score: Decimal,
    ) -> Decimal:
        weighted_score = (
            rule_score * RULE_SCORE_WEIGHT
            + anomaly_score * ANOMALY_SCORE_WEIGHT
        )
        return RiskService._quantize_score(weighted_score)

    @staticmethod
    def _quantize_score(score: Decimal) -> Decimal:
        if score < Decimal("0"):
            score = Decimal("0")
        if score > Decimal("1"):
            score = Decimal("1")

        return score.quantize(SCORE_QUANTIZER)

    @staticmethod
    def _map_score_to_outcome(
        combined_score: Decimal,
    ) -> tuple[RiskLevel, RiskDecision]:
        if combined_score >= HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH, RiskDecision.REJECT

        if combined_score >= LOW_RISK_THRESHOLD:
            return RiskLevel.MEDIUM, RiskDecision.WARN

        return RiskLevel.LOW, RiskDecision.ALLOW
