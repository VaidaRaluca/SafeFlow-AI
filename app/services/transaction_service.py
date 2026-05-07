import uuid

from sqlalchemy.orm import Session

from app.repositories.transaction_repository import TransactionRepository
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionDetailResponse, TransactionListResponse


class TransactionServiceError(Exception):
    """Base error for transaction history/detail operations."""


class TransactionNotFoundError(TransactionServiceError):
    """Raised when the requested transaction does not exist."""


class TransactionForbiddenError(TransactionServiceError):
    """Raised when the current account cannot view a transaction."""


class TransactionService:
    def __init__(self, db: Session) -> None:
        self.transaction_repository = TransactionRepository(db)

    def get_current_account_transactions(
        self,
        account: AccountResponse,
    ) -> TransactionListResponse:
        transactions = self.transaction_repository.get_transactions_for_account(
            account.id,
        )
        return TransactionListResponse(transactions=transactions)

    def get_transaction_details(
        self,
        transaction_id: uuid.UUID,
        account: AccountResponse,
    ) -> TransactionDetailResponse:
        transaction = self.transaction_repository.get_transaction_details(
            transaction_id,
        )

        if transaction is None:
            raise TransactionNotFoundError("Transaction was not found.")

        if transaction.sender_id != account.id and transaction.receiver_id != account.id:
            raise TransactionForbiddenError(
                "This transaction belongs to another account."
            )

        return transaction
