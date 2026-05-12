import uuid
import unicodedata
from datetime import UTC, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.repositories.contact_repository import ContactRepository
from app.repositories.transaction_repository import TransactionRepository


MAX_RULE_SCORE = Decimal("1.00")
MIN_RULE_SCORE = Decimal("0.00")

NEW_BENEFICIARY_HIGH_AMOUNT_WEIGHT = Decimal("0.40")
URGENCY_SOCIAL_ENGINEERING_WEIGHT = Decimal("0.35")
GRADUAL_TRUST_BUILDING_WEIGHT = Decimal("0.50")

NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 5
RISK_TIMEZONE = ZoneInfo("Europe/Bucharest")

HIGH_AMOUNT_FLOOR = Decimal("1000.00")
SMALL_TRANSFER_THRESHOLD = Decimal("100.00")
GRADUAL_LARGE_TRANSFER_THRESHOLD = Decimal("1000.00")
MIN_SMALL_TRANSFER_COUNT = 3

SUSPICIOUS_KEYWORDS = (
    "urgent",
    "immediately",
    "asap",
    "transfer now",
    "today only",
    "verify account",
    "verification",
    "account blocked",
    "account locked",
    "unlock account",
    "password",
    "otp",
    "2fa",
    "security code",
    "pin code",
    "gift card",
    "crypto",
    "bitcoin",
    "wallet",
    "wire transfer",
    "family emergency",
    "medical emergency",
    "hospital",
    "bail",
    "lawyer",
    "prize",
    "lottery",
    "refund",
    "tax payment",
    "new bank details",
    "invoice changed",
    "imediat",
    "verificare",
    "cont blocat",
    "cont inchis",
    "deblocare cont",
    "parola",
    "cod securitate",
    "cod otp",
    "card cadou",
    "cripto",
    "urgenta familie",
    "spital",
    "premiu",
    "rambursare",
    "anaf",
    "factura modificata",
    "cont nou",
)

class RuleScoreService:

    @staticmethod
    def calculate_rule_score(
        db: Session,
        transaction_id: uuid.UUID,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        amount: Decimal,
        description: str | None,
        created_at: datetime,
    ) -> Decimal:
        score = Decimal("0")
        transaction_repository = TransactionRepository(db)

        is_trusted = ContactRepository.is_receiver_trusted(db, sender_id, receiver_id)

        # Trust reduces the "new beneficiary" concern, but it must not disable
        # fraud signals that can happen after trust is established.
        if not is_trusted:
            previous_transactions_count = (
                transaction_repository.count_previous_transactions_to_receiver(
                    sender_account_id=sender_id,
                    receiver_account_id=receiver_id,
                    exclude_transaction_id=transaction_id,
                )
            )
            sender_average_amount = (
                transaction_repository.get_sender_average_transaction_amount(
                    sender_account_id=sender_id,
                    exclude_transaction_id=transaction_id,
                )
            )

            high_amount = (
                amount >= HIGH_AMOUNT_FLOOR
                or (
                    sender_average_amount > Decimal("0")
                    and amount >= sender_average_amount * Decimal("2.00")
                )
            )

            if previous_transactions_count == 0 and high_amount:
                score += NEW_BENEFICIARY_HIGH_AMOUNT_WEIGHT

        # Rule 3: Gradual trust-building / trust abuse
        small_transfers_count = transaction_repository.count_small_transactions_to_receiver(
            sender_account_id=sender_id,
            receiver_account_id=receiver_id,
            threshold=SMALL_TRANSFER_THRESHOLD,
            exclude_transaction_id=transaction_id,
        )

        is_large_current_transfer = amount >= GRADUAL_LARGE_TRANSFER_THRESHOLD
        has_gradual_pattern = small_transfers_count >= MIN_SMALL_TRANSFER_COUNT

        # Rule 2: Urgency / social engineering. Night-time is contextual:
        # it should escalate large transfers, but not double-count a gradual
        # trust-abuse pattern unless the description also shows pressure.
        is_night_time = RuleScoreService._is_night_time(created_at)
        has_suspicious_keywords = RuleScoreService._has_suspicious_keywords(description)
        night_high_amount = (
            is_night_time
            and amount >= HIGH_AMOUNT_FLOOR
            and not has_gradual_pattern
        )

        if has_suspicious_keywords or night_high_amount:
            score += URGENCY_SOCIAL_ENGINEERING_WEIGHT

        if has_gradual_pattern and is_large_current_transfer:
            score += GRADUAL_TRUST_BUILDING_WEIGHT

        return RuleScoreService._clamp_score(score)

    @staticmethod
    def _is_night_time(created_at: datetime) -> bool:
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            created_at = created_at.replace(tzinfo=UTC)

        hour = created_at.astimezone(RISK_TIMEZONE).hour
        return hour >= NIGHT_START_HOUR or hour < NIGHT_END_HOUR

    @staticmethod
    def _has_suspicious_keywords(description: str | None) -> bool:
        if not description:
            return False
        normalized_description = RuleScoreService._normalize_text(description)
        return any(keyword in normalized_description for keyword in SUSPICIOUS_KEYWORDS)

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.casefold())
        return "".join(char for char in normalized if not unicodedata.combining(char))

    @staticmethod
    def _clamp_score(score: Decimal) -> Decimal:
        if score < MIN_RULE_SCORE:
            return MIN_RULE_SCORE
        if score > MAX_RULE_SCORE:
            return MAX_RULE_SCORE
        return score
