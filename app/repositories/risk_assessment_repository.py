import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import RiskDecision, RiskLevel
from app.models.risk_assessment import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse


class RiskAssessmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_risk_assessment(
        self,
        transaction_id: uuid.UUID,
        rule_score: Decimal,
        anomaly_score: Decimal,
        combined_score: Decimal,
        risk_level: RiskLevel,
        decision: RiskDecision,
        evaluated_at: datetime,
    ) -> RiskAssessmentResponse:
        existing_assessment = self.db.scalar(
            select(RiskAssessment).where(
                RiskAssessment.transaction_id == transaction_id,
            )
        )

        if existing_assessment is None:
            assessment = RiskAssessment(
                transaction_id=transaction_id,
                rule_score=rule_score,
                anomaly_score=anomaly_score,
                combined_score=combined_score,
                risk_level=risk_level,
                decision=decision,
                evaluated_at=evaluated_at,
            )
            self.db.add(assessment)
        else:
            assessment = existing_assessment
            assessment.rule_score = rule_score
            assessment.anomaly_score = anomaly_score
            assessment.combined_score = combined_score
            assessment.risk_level = risk_level
            assessment.decision = decision
            assessment.evaluated_at = evaluated_at

        self.db.flush()
        self.db.refresh(assessment)
        return RiskAssessmentResponse.model_validate(assessment)

    def get_risk_assessment_by_transaction_id(
        self,
        transaction_id: uuid.UUID,
    ) -> RiskAssessmentResponse | None:
        assessment = self.db.scalar(
            select(RiskAssessment).where(
                RiskAssessment.transaction_id == transaction_id,
            )
        )

        if assessment is None:
            return None

        return RiskAssessmentResponse.model_validate(assessment)
