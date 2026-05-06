import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.contact_repository import ContactRepository
from app.repositories.transaction_repository import TransactionRepository


MAX_RULE_SCORE = Decimal("1.00")
MIN_RULE_SCORE = Decimal("0.00")

NEW_BENEFICIARY_HIGH_AMOUNT_WEIGHT = Decimal("0.40")
URGENCY_SOCIAL_ENGINEERING_WEIGHT = Decimal("0.35")
GRADUAL_TRUST_BUILDING_WEIGHT = Decimal("0.25")

NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 5

HIGH_AMOUNT_FLOOR = Decimal("1000.00")
SMALL_TRANSFER_THRESHOLD = Decimal("100.00")
GRADUAL_LARGE_TRANSFER_THRESHOLD = Decimal("1000.00")
MIN_SMALL_TRANSFER_COUNT = 3

SUSPICIOUS_KEYWORDS = (
    "urgent",
    "immediately",
    "asap",
    "verify",
    "verification",
    "blocked",
    "unlock",
    "security",
    "account",
    "transfer now",
    "family emergency",
    "hospital",
    "tax",
    "prize",
)

REASON_NEW_BENEFICIARY_HIGH_AMOUNT = "new_beneficiary_high_amount"
REASON_URGENCY_NIGHT_TIME = "urgency_night_time"
REASON_URGENCY_SUSPICIOUS_KEYWORD = "urgency_suspicious_keyword"
REASON_GRADUAL_TRUST_BUILDING = "gradual_trust_building"
REASON_TRUSTED_BENEFICIARY = "trusted_beneficiary"


class RuleScoreService:

    @staticmethod
    def calculate_rule_score(
        db: Session,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        amount: Decimal,
        description: str | None,
        created_at: datetime,
    ) -> tuple[Decimal, list[str]]:
        score = Decimal("0")
        reason_codes: list[str] = []
        transaction_repository = TransactionRepository(db)

        is_trusted = ContactRepository.is_receiver_trusted(db, sender_id, receiver_id)

        if is_trusted:
            reason_codes.append(REASON_TRUSTED_BENEFICIARY)
        else:
            # Rule 1: New beneficiary + high amount
            previous_transactions_count = (
                transaction_repository.get_previous_transactions_to_receiver_for_features(
                    sender_id,
                    receiver_id,
                )
            )
            sender_statistics = transaction_repository.get_sender_transaction_statistics(sender_id)
            sender_average_amount = sender_statistics["avg_amount"] or Decimal("0")

            high_amount = (
                amount >= HIGH_AMOUNT_FLOOR
                or (
                    sender_average_amount > Decimal("0")
                    and amount >= sender_average_amount * Decimal("2.00")
                )
            )

            if previous_transactions_count == 0 and high_amount:
                score += NEW_BENEFICIARY_HIGH_AMOUNT_WEIGHT
                reason_codes.append(REASON_NEW_BENEFICIARY_HIGH_AMOUNT)

            # Rule 2: Urgency / social engineering
            is_night_time = RuleScoreService._is_night_time(created_at)
            has_suspicious_keywords = RuleScoreService._has_suspicious_keywords(description)

            if is_night_time or has_suspicious_keywords:
                score += URGENCY_SOCIAL_ENGINEERING_WEIGHT
                if is_night_time:
                    reason_codes.append(REASON_URGENCY_NIGHT_TIME)
                if has_suspicious_keywords:
                    reason_codes.append(REASON_URGENCY_SUSPICIOUS_KEYWORD)

            # Rule 3: Gradual trust-building
            small_transfers_count = transaction_repository.get_small_transaction_count_to_receiver_for_features(
                sender_id,
                receiver_id,
                SMALL_TRANSFER_THRESHOLD,
            )

            is_large_current_transfer = amount >= GRADUAL_LARGE_TRANSFER_THRESHOLD
            has_gradual_pattern = small_transfers_count >= MIN_SMALL_TRANSFER_COUNT

            if has_gradual_pattern and is_large_current_transfer:
                score += GRADUAL_TRUST_BUILDING_WEIGHT
                reason_codes.append(REASON_GRADUAL_TRUST_BUILDING)

        return RuleScoreService._clamp_score(score), reason_codes

    @staticmethod
    def _is_night_time(created_at: datetime) -> bool:
        hour = created_at.hour
        return hour >= NIGHT_START_HOUR or hour < NIGHT_END_HOUR

    @staticmethod
    def _has_suspicious_keywords(description: str | None) -> bool:
        if not description:
            return False
        normalized_description = description.lower()
        return any(keyword in normalized_description for keyword in SUSPICIOUS_KEYWORDS)

    @staticmethod
    def _clamp_score(score: Decimal) -> Decimal:
        if score < MIN_RULE_SCORE:
            return MIN_RULE_SCORE
        if score > MAX_RULE_SCORE:
            return MAX_RULE_SCORE
        return score
