import uuid
from collections.abc import Callable

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories import transaction_repository
from app.repositories.account_repository import AccountRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.account import AccountResponse
from app.schemas.payment import PaymentCancel, PaymentConfirm, PaymentCreate
from app.schemas.transaction import TransactionDetailResponse
from app.services import risk_service, settlement_service


WARNED_STATUS = "WARNED"
SETTLED_STATUS = "SETTLED"
CANCELED_STATUS = "CANCELED"
REJECTED_STATUS = "REJECTED"

LOW_RISK_LEVEL = "LOW"
MEDIUM_RISK_LEVEL = "MEDIUM"
HIGH_RISK_LEVEL = "HIGH"

PasswordVerifier = Callable[[AccountResponse, str], bool]


class PaymentServiceError(Exception):
    """Base error for Andrei-owned payment lifecycle orchestration."""


class PaymentDependencyNotReadyError(PaymentServiceError):
    """Raised when a teammate-owned integration point is not implemented yet."""


class PaymentNotFoundError(PaymentServiceError):
    """Raised when the requested payment transaction does not exist."""


class PaymentForbiddenError(PaymentServiceError):
    """Raised when the current account cannot operate on the payment."""


class PaymentValidationError(PaymentServiceError):
    """Raised when payment input or state is invalid."""


class PaymentConflictError(PaymentServiceError):
    """Raised when the requested lifecycle action conflicts with current state."""


def create_payment(
    db: Session,
    sender_account: AccountResponse,
    payment: PaymentCreate,
) -> TransactionDetailResponse:
    receiver_account = _resolve_receiver_account(db=db, payment=payment)

    if sender_account.id == receiver_account.id:
        raise PaymentValidationError("Sender and receiver accounts must be different.")

    if sender_account.currency != payment.currency:
        raise PaymentValidationError("Payment currency must match the sender account.")

    if receiver_account.currency != payment.currency:
        raise PaymentValidationError("Payment currency must match the receiver account.")

    if sender_account.balance < payment.amount:
        raise PaymentValidationError("Insufficient funds for this payment.")

    try:
        transaction = transaction_repository.create_pending_transaction(
            db=db,
            sender_id=sender_account.id,
            receiver_id=receiver_account.id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
        )
        _ensure_contact_exists(
            db=db,
            sender_id=sender_account.id,
            receiver_id=receiver_account.id,
        )
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise PaymentValidationError("Could not create the pending payment.") from exc

    try:
        risk_evaluation = _evaluate_transaction_risk(db=db, transaction=transaction)
        risk_level = _extract_risk_level(
            risk_evaluation=risk_evaluation,
            transaction=transaction,
        )
    except PaymentDependencyNotReadyError:
        return transaction

    try:
        transaction = _apply_risk_level(
            db=db,
            transaction=transaction,
            risk_level=risk_level,
        )
        db.commit()
        return transaction
    except settlement_service.SettlementError as exc:
        db.rollback()
        raise PaymentConflictError(str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise PaymentValidationError(
            "Could not update the payment after risk evaluation."
        ) from exc


def confirm_payment(
    db: Session,
    transaction_id: uuid.UUID,
    sender_account: AccountResponse,
    confirmation: PaymentConfirm,
    password_verifier: PasswordVerifier | None = None,
) -> TransactionDetailResponse:
    transaction = transaction_repository.get_transaction_for_update(
        db=db,
        transaction_id=transaction_id,
    )

    if transaction is None:
        raise PaymentNotFoundError("Payment was not found.")

    _ensure_sender_owns_transaction(
        transaction=transaction,
        sender_account=sender_account,
    )

    status = _enum_value(transaction.status)

    if status != WARNED_STATUS:
        raise PaymentConflictError(
            "Only warned payments can be confirmed."
        )

    _verify_warned_payment_password(
        sender_account=sender_account,
        confirmation=confirmation,
        password_verifier=password_verifier,
    )

    try:
        settled_transaction = settlement_service.settle_transaction(
            db=db,
            transaction=transaction,
        )
        db.commit()
        return settled_transaction
    except settlement_service.SettlementError as exc:
        db.rollback()
        raise PaymentConflictError(str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise PaymentValidationError("Could not settle the payment.") from exc


def cancel_payment(
    db: Session,
    transaction_id: uuid.UUID,
    sender_account: AccountResponse,
    cancellation: PaymentCancel,
) -> TransactionDetailResponse:
    transaction = transaction_repository.get_transaction_for_update(
        db=db,
        transaction_id=transaction_id,
    )

    if transaction is None:
        raise PaymentNotFoundError("Payment was not found.")

    _ensure_sender_owns_transaction(
        transaction=transaction,
        sender_account=sender_account,
    )

    if _enum_value(transaction.status) in {
        SETTLED_STATUS,
        CANCELED_STATUS,
        REJECTED_STATUS,
    }:
        raise PaymentConflictError(
            "Settled, canceled, or rejected payments cannot be canceled."
        )

    try:
        canceled_transaction = transaction_repository.mark_transaction_as_canceled(
            db=db,
            transaction_id=transaction.id,
        )
        db.commit()

        if canceled_transaction is None:
            raise PaymentNotFoundError("Payment was not found.")

        detailed_transaction = TransactionRepository(db).get_transaction_details(
            canceled_transaction.id,
        )

        if detailed_transaction is None:
            raise PaymentNotFoundError("Payment was not found.")

        return detailed_transaction
    except SQLAlchemyError as exc:
        db.rollback()
        raise PaymentValidationError("Could not cancel the payment.") from exc


def _evaluate_transaction_risk(
    db: Session,
    transaction: TransactionDetailResponse,
) -> object:
    evaluator = getattr(risk_service, "evaluate_transaction", None)

    if evaluator is not None:
        return evaluator(db=db, transaction=transaction)

    service_evaluator = getattr(
        getattr(risk_service, "RiskService", None),
        "evaluate_transaction_risk",
        None,
    )

    if service_evaluator is not None:
        return service_evaluator(
            db=db,
            transaction_id=transaction.id,
            sender_id=transaction.sender_id,
            receiver_id=transaction.receiver_id,
            amount=transaction.amount,
            description=transaction.description,
            created_at=transaction.created_at,
        )

    raise PaymentDependencyNotReadyError(
        "Risk evaluation is owned by the risk team and is not implemented yet."
    )


def _resolve_receiver_account(
    db: Session,
    payment: PaymentCreate,
) -> AccountResponse:
    account_repository = AccountRepository(db)

    if payment.receiver_id is not None:
        receiver_account = account_repository.get_account_by_id(payment.receiver_id)
    elif payment.receiver_iban is not None:
        receiver_account = account_repository.get_account_by_iban(payment.receiver_iban)
    else:
        receiver_account = None

    if receiver_account is None:
        raise PaymentValidationError("Receiver account was not found.")

    return receiver_account


def _ensure_contact_exists(
    db: Session,
    sender_id: uuid.UUID,
    receiver_id: uuid.UUID,
) -> None:
    ContactRepository.create_contact(
        db=db,
        sender_id=sender_id,
        receiver_id=receiver_id,
    )


def _extract_risk_level(
    risk_evaluation: object,
    transaction: TransactionDetailResponse,
) -> str:
    raw_level = None

    if isinstance(risk_evaluation, dict):
        raw_level = risk_evaluation.get("risk_level")
    else:
        raw_level = getattr(risk_evaluation, "risk_level", None)

    if raw_level is None and transaction.risk_assessment is not None:
        raw_level = transaction.risk_assessment.risk_level

    if raw_level is None:
        raise PaymentDependencyNotReadyError(
            "Risk evaluation did not return a risk level."
        )

    risk_level = _enum_value(raw_level)

    if risk_level not in {
        LOW_RISK_LEVEL,
        MEDIUM_RISK_LEVEL,
        HIGH_RISK_LEVEL,
    }:
        raise PaymentDependencyNotReadyError(
            "Risk evaluation returned an unsupported risk level."
        )

    return risk_level


def _apply_risk_level(
    db: Session,
    transaction: TransactionDetailResponse,
    risk_level: str,
) -> TransactionDetailResponse:
    if risk_level == LOW_RISK_LEVEL:
        transaction_repository.mark_transaction_as_approved(
            db=db,
            transaction_id=transaction.id,
        )
        updated_transaction = transaction_repository.set_requires_password_confirmation(
            db=db,
            transaction_id=transaction.id,
            requires_password_confirmation=False,
        )
        if updated_transaction is None:
            raise PaymentNotFoundError("Payment was not found.")

        return settlement_service.settle_transaction(
            db=db,
            transaction=updated_transaction,
        )
    elif risk_level == MEDIUM_RISK_LEVEL:
        transaction_repository.mark_transaction_as_warned(
            db=db,
            transaction_id=transaction.id,
        )
        updated_transaction = transaction_repository.set_requires_password_confirmation(
            db=db,
            transaction_id=transaction.id,
            requires_password_confirmation=True,
        )
    else:
        transaction_repository.mark_transaction_as_rejected(
            db=db,
            transaction_id=transaction.id,
        )
        updated_transaction = transaction_repository.set_requires_password_confirmation(
            db=db,
            transaction_id=transaction.id,
            requires_password_confirmation=False,
        )

    if updated_transaction is None:
        raise PaymentNotFoundError("Payment was not found.")

    detailed_transaction = TransactionRepository(db).get_transaction_details(
        updated_transaction.id,
    )

    if detailed_transaction is None:
        raise PaymentNotFoundError("Payment was not found.")

    return detailed_transaction


def _ensure_sender_owns_transaction(
    transaction: TransactionDetailResponse,
    sender_account: AccountResponse,
) -> None:
    if transaction.sender_id != sender_account.id:
        raise PaymentForbiddenError("This payment belongs to another account.")


def _verify_warned_payment_password(
    sender_account: AccountResponse,
    confirmation: PaymentConfirm,
    password_verifier: PasswordVerifier | None,
) -> None:
    if not confirmation.password:
        raise PaymentValidationError(
            "Password is required to confirm a warned payment."
        )

    if password_verifier is None:
        raise PaymentDependencyNotReadyError(
            "Password verification is owned by auth and is not implemented yet."
        )

    if not password_verifier(sender_account, confirmation.password):
        raise PaymentForbiddenError("Password confirmation failed.")


def _enum_value(value: object) -> str:
    raw_value = getattr(value, "value", value)
    return str(raw_value).upper()
