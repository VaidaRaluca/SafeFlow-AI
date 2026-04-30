import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.account import AccountResponse
from app.schemas.payment import PaymentCancel, PaymentConfirm, PaymentCreate
from app.schemas.transaction import TransactionDetailResponse
from app.services import payment_service


router = APIRouter(prefix="/api/payments", tags=["payments"])


def get_current_payment_account() -> AccountResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Current account authentication is owned by User & Account Management "
            "and is not implemented yet."
        ),
    )


@router.post(
    "",
    response_model=TransactionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_account: AccountResponse = Depends(get_current_payment_account),
):
    try:
        return payment_service.create_payment(
            db=db,
            sender_account=current_account,
            payment=payment,
        )
    except payment_service.PaymentServiceError as exc:
        raise _to_http_exception(exc) from exc


@router.post(
    "/{payment_id}/confirm",
    response_model=TransactionDetailResponse,
)
def confirm_payment(
    payment_id: uuid.UUID,
    confirmation: PaymentConfirm,
    db: Session = Depends(get_db),
    current_account: AccountResponse = Depends(get_current_payment_account),
):
    try:
        return payment_service.confirm_payment(
            db=db,
            transaction_id=payment_id,
            sender_account=current_account,
            confirmation=confirmation,
        )
    except payment_service.PaymentServiceError as exc:
        raise _to_http_exception(exc) from exc


@router.post(
    "/{payment_id}/cancel",
    response_model=TransactionDetailResponse,
)
def cancel_payment(
    payment_id: uuid.UUID,
    cancellation: PaymentCancel,
    db: Session = Depends(get_db),
    current_account: AccountResponse = Depends(get_current_payment_account),
):
    try:
        return payment_service.cancel_payment(
            db=db,
            transaction_id=payment_id,
            sender_account=current_account,
            cancellation=cancellation,
        )
    except payment_service.PaymentServiceError as exc:
        raise _to_http_exception(exc) from exc


def _to_http_exception(exc: payment_service.PaymentServiceError) -> HTTPException:
    if isinstance(exc, payment_service.PaymentDependencyNotReadyError):
        return HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        )

    if isinstance(exc, payment_service.PaymentNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if isinstance(exc, payment_service.PaymentForbiddenError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    if isinstance(exc, payment_service.PaymentConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
