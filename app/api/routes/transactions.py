import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionDetailResponse, TransactionListResponse
from app.schemas.user import UserResponse
from app.services.account_service import AccountService
from app.services.transaction_service import (
    TransactionForbiddenError,
    TransactionNotFoundError,
    TransactionService,
    TransactionServiceError,
)


router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def get_current_transaction_account(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountResponse:
    return AccountService(db).get_current_account(current_user.id)


@router.get("/me", response_model=TransactionListResponse)
def get_my_transactions(
    db: Session = Depends(get_db),
    current_account: AccountResponse = Depends(get_current_transaction_account),
) -> TransactionListResponse:
    try:
        return TransactionService(db).get_current_account_transactions(
            current_account,
        )
    except TransactionServiceError as exc:
        raise _to_http_exception(exc) from exc


@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction_details(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_account: AccountResponse = Depends(get_current_transaction_account),
) -> TransactionDetailResponse:
    try:
        return TransactionService(db).get_transaction_details(
            transaction_id=transaction_id,
            account=current_account,
        )
    except TransactionServiceError as exc:
        raise _to_http_exception(exc) from exc


def _to_http_exception(exc: TransactionServiceError) -> HTTPException:
    if isinstance(exc, TransactionNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if isinstance(exc, TransactionForbiddenError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
