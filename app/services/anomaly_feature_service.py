from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository


NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 5

DEFAULT_DAYS_SINCE_LAST_RECEIVER_TRANSACTION = 999.0
SMALL_TRANSFER_THRESHOLD = Decimal("100.00")

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
    "emergency",
    "gift card",
    "crypto",
    "password",
    "help",
)


FEATURE_COLUMNS = [
    "amount",
    "amount_to_sender_average_ratio",
    "amount_to_sender_median_ratio",
    "amount_to_sender_max_ratio",
    "sender_transaction_count",
    "sender_safe_transaction_count",
    "previous_transactions_to_receiver",
    "is_new_receiver",
    "days_since_last_transaction_to_receiver",
    "small_transaction_count_to_receiver",
    "hour_of_day",
    "is_night_transaction",
    "description_risk_keyword_count",
]


class AnomalyFeatureService:
    def __init__(self, db: Session) -> None:
        self.transaction_repository = TransactionRepository(db)

    def build_global_training_dataset(self) -> list[dict[str, float]]:
        safe_transactions = (
            self.transaction_repository.get_all_safe_transactions_for_training()
        )

        return [
            self.build_feature_row(transaction)
            for transaction in safe_transactions
        ]

    def build_feature_row(self, transaction: Transaction) -> dict[str, float]:

        sender_id = transaction.sender_id
        receiver_id = transaction.receiver_id
        amount = transaction.amount

        sender_statistics = self.transaction_repository.get_sender_transaction_statistics(
            sender_id
        )

        sender_median_amount = (
            self.transaction_repository.get_sender_median_transaction_amount(
                sender_id
            )
        )

        previous_transactions_to_receiver = (
            self.transaction_repository.get_previous_transactions_to_receiver_for_features(
                sender_id,
                receiver_id,
            )
        )

        days_since_last_transaction = (
            self.transaction_repository.get_days_since_last_transaction_to_receiver(
                sender_id,
                receiver_id,
            )
        )

        small_transaction_count = (
            self.transaction_repository.get_small_transaction_count_to_receiver_for_features(
                sender_id,
                receiver_id,
                SMALL_TRANSFER_THRESHOLD,
            )
        )

        sender_safe_transaction_count = (
            self.transaction_repository.get_sender_safe_transaction_count(sender_id)
        )

        avg_amount = sender_statistics["avg_amount"] or Decimal("0.00")
        max_amount = sender_statistics["max_amount"] or Decimal("0.00")
        median_amount = sender_median_amount or Decimal("0.00")

        hour_of_day = self.extract_hour_of_day(transaction.created_at)

        feature_row = {
            "amount": float(amount),
            "amount_to_sender_average_ratio": self.safe_ratio(amount, avg_amount),
            "amount_to_sender_median_ratio": self.safe_ratio(amount, median_amount),
            "amount_to_sender_max_ratio": self.safe_ratio(amount, max_amount),
            "sender_transaction_count": float(sender_statistics["count"] or 0),
            "sender_safe_transaction_count": float(sender_safe_transaction_count),
            "previous_transactions_to_receiver": float(previous_transactions_to_receiver),
            "is_new_receiver": self.calculate_is_new_receiver(
                previous_transactions_to_receiver
            ),
            "days_since_last_transaction_to_receiver": float(
                days_since_last_transaction
                if days_since_last_transaction is not None
                else DEFAULT_DAYS_SINCE_LAST_RECEIVER_TRANSACTION
            ),
            "small_transaction_count_to_receiver": float(small_transaction_count),
            "hour_of_day": float(hour_of_day),
            "is_night_transaction": self.calculate_is_night_transaction(hour_of_day),
            "description_risk_keyword_count": float(
                self.count_description_risk_keywords(transaction.description)
            ),
        }

        return self._order_feature_row(feature_row)

    @staticmethod
    def get_feature_columns() -> list[str]:
        return FEATURE_COLUMNS.copy()

    @staticmethod
    def safe_ratio(
        numerator: Decimal,
        denominator: Decimal | None,
    ) -> float:
        if denominator is None or denominator == Decimal("0"):
            return 0.0

        return float(numerator / denominator)

    @staticmethod
    def calculate_is_new_receiver(
        previous_transactions_to_receiver: int,
    ) -> float:
        return 1.0 if previous_transactions_to_receiver == 0 else 0.0

    @staticmethod
    def extract_hour_of_day(created_at: datetime) -> int:
        return created_at.hour

    @staticmethod
    def calculate_is_night_transaction(hour_of_day: int) -> float:
        return 1.0 if hour_of_day >= NIGHT_START_HOUR or hour_of_day < NIGHT_END_HOUR else 0.0

    @staticmethod
    def count_description_risk_keywords(description: str | None) -> int:
        if not description:
            return 0

        normalized_description = description.lower()

        return sum(
            1
            for keyword in SUSPICIOUS_KEYWORDS
            if keyword in normalized_description
        )

    @staticmethod
    def _order_feature_row(
        feature_row: dict[str, Any],
    ) -> dict[str, float]:
        return {
            column: float(feature_row[column])
            for column in FEATURE_COLUMNS
        }