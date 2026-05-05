import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.db.session import SessionLocal
from app.models.enums import CurrencyCode, TransactionStatus
from app.models.transaction import Transaction
from app.services.anomaly_score_service import AnomalyScoreService



def main() -> None:
    if len(sys.argv) >= 5:
        sender_account_id = uuid.UUID(sys.argv[1])
        receiver_account_id = uuid.UUID(sys.argv[2])
        amount = Decimal(sys.argv[3])
        description = sys.argv[4]
    else:
        sender_account_id = uuid.UUID(DEFAULT_SENDER_ACCOUNT_ID)
        receiver_account_id = uuid.UUID(DEFAULT_RECEIVER_ACCOUNT_ID)
        amount = Decimal(DEFAULT_AMOUNT)
        description = DEFAULT_DESCRIPTION

        print("No arguments provided. Using default test transaction.")
        print()

    db = SessionLocal()

    try:
        transaction = Transaction(
            id=uuid.uuid4(),
            sender_id=sender_account_id,
            receiver_id=receiver_account_id,
            amount=amount,
            currency=CurrencyCode.EUR,
            description=description,
            status=TransactionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            requires_password_confirmation=False,
        )

        anomaly_service = AnomalyScoreService(db)
        anomaly_score = anomaly_service.calculate_anomaly_score(transaction)

        print("Anomaly score result")
        print("--------------------")
        print(f"Temporary transaction ID: {transaction.id}")
        print(f"Sender account ID: {sender_account_id}")
        print(f"Receiver account ID: {receiver_account_id}")
        print(f"Amount: {amount}")
        print(f"Description: {description}")
        print(f"Status: {transaction.status}")
        print(f"Created at: {transaction.created_at}")
        print(f"Anomaly score: {anomaly_score}")

    finally:
        db.close()


if __name__ == "__main__":
    main()

# Run anomaly 1
# python -m scripts.test_new_transaction \
# 41df0de8-897d-47c4-8894-7c45d5a14bb2 \
# 000a46e2-c40d-4f89-9fa1-fd08059f509c \
# 450.00 \
# "invoice"

# Run anomaly 2
# python -m scripts.test_new_transaction \
# 41df0de8-897d-47c4-8894-7c45d5a14bb2 \
# 000a46e2-c40d-4f89-9fa1-fd08059f509c \
# 1500.00 \
# "urgent crypto transfer"

# Run normal transaction
# python -m scripts.test_new_transaction \
# 41df0de8-897d-47c4-8894-7c45d5a14bb2 \
# 000a46e2-c40d-4f89-9fa1-fd08059f509c \
# 50.00 \
# "lunch"