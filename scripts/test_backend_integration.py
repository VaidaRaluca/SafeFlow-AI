import uuid
from collections.abc import Callable
from decimal import Decimal

import psycopg
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import RiskDecision, RiskLevel
from app.db.session import SessionLocal
from app.main import app
from app.repositories.account_repository import AccountRepository
from app.repositories.risk_assessment_repository import RiskAssessmentRepository
from app.services import payment_service, risk_service


PASSWORD = "SafeFlow123!"


def main() -> None:
    _assert_database_available()
    client = TestClient(app)
    suffix = uuid.uuid4().hex

    sender = _register_and_login(
        client=client,
        full_name="Integration Sender",
        email=f"sender-{suffix}@safeflow-demo.com",
    )
    receiver = _register_and_login(
        client=client,
        full_name="Integration Receiver",
        email=f"receiver-{suffix}@safeflow-demo.com",
    )

    sender_account = _get_account(client, sender["access_token"])
    receiver_account = _get_account(client, receiver["access_token"])
    _fund_account(sender_account["id"], Decimal("10000.00"))

    low_payment = _create_payment_with_risk(
        client=client,
        token=sender["access_token"],
        receiver_iban=receiver_account["iban"],
        amount="25.00",
        risk_level=RiskLevel.LOW,
    )
    assert low_payment["status"] == "SETTLED"
    assert low_payment["risk_assessment"]["risk_level"] == "LOW"
    assert low_payment["settled_at"] is not None

    medium_payment = _create_payment_with_risk(
        client=client,
        token=sender["access_token"],
        receiver_iban=receiver_account["iban"],
        amount="35.00",
        risk_level=RiskLevel.MEDIUM,
    )
    assert medium_payment["status"] == "WARNED"
    assert medium_payment["requires_password_confirmation"] is True

    wrong_password_response = client.post(
        f"/api/payments/{medium_payment['id']}/confirm",
        json={"password": "wrong-password"},
        headers=_auth_header(sender["access_token"]),
    )
    assert wrong_password_response.status_code == 403

    settled_medium = _confirm_payment(
        client=client,
        token=sender["access_token"],
        payment_id=medium_payment["id"],
        password=PASSWORD,
    )
    assert settled_medium["status"] == "SETTLED"

    high_payment = _create_payment_with_risk(
        client=client,
        token=sender["access_token"],
        receiver_iban=receiver_account["iban"],
        amount="1500.00",
        risk_level=RiskLevel.HIGH,
    )
    assert high_payment["status"] == "REJECTED"

    rejected_confirm_response = client.post(
        f"/api/payments/{high_payment['id']}/confirm",
        json={},
        headers=_auth_header(sender["access_token"]),
    )
    assert rejected_confirm_response.status_code == 409

    pending_payment = _create_pending_payment(
        client=client,
        token=sender["access_token"],
        receiver_iban=receiver_account["iban"],
        amount="10.00",
    )
    assert pending_payment["status"] == "PENDING"
    assert _cancel_payment(client, sender["access_token"], pending_payment["id"])["status"] == "CANCELED"

    auto_settled_to_cancel = _create_payment_with_risk(
        client=client,
        token=sender["access_token"],
        receiver_iban=receiver_account["iban"],
        amount="15.00",
        risk_level=RiskLevel.LOW,
    )
    assert auto_settled_to_cancel["status"] == "SETTLED"
    settled_cancel_response = client.post(
        f"/api/payments/{auto_settled_to_cancel['id']}/cancel",
        json={},
        headers=_auth_header(sender["access_token"]),
    )
    assert settled_cancel_response.status_code == 409

    warned_to_cancel = _create_payment_with_risk(
        client=client,
        token=sender["access_token"],
        receiver_iban=receiver_account["iban"],
        amount="20.00",
        risk_level=RiskLevel.MEDIUM,
    )
    assert _cancel_payment(client, sender["access_token"], warned_to_cancel["id"])["status"] == "CANCELED"

    sender_history = client.get(
        "/api/transactions/me",
        headers=_auth_header(sender["access_token"]),
    )
    assert sender_history.status_code == 200
    assert len(sender_history.json()["transactions"]) >= 6

    receiver_history = client.get(
        "/api/transactions/me",
        headers=_auth_header(receiver["access_token"]),
    )
    assert receiver_history.status_code == 200
    assert len(receiver_history.json()["transactions"]) >= 6

    detail_response = client.get(
        f"/api/transactions/{low_payment['id']}",
        headers=_auth_header(sender["access_token"]),
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["settled_at"] is not None

    sender_balance = Decimal(_get_account(client, sender["access_token"])["balance"])
    receiver_balance = Decimal(_get_account(client, receiver["access_token"])["balance"])
    assert sender_balance == Decimal("9925.00")
    assert receiver_balance == Decimal("75.00")

    print("Backend integration checks passed.")


def _register_and_login(
    client: TestClient,
    full_name: str,
    email: str,
) -> dict[str, str]:
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": PASSWORD,
        },
    )
    assert login_response.status_code == 200, login_response.text
    return login_response.json()


def _get_account(client: TestClient, token: str) -> dict:
    response = client.get("/api/accounts/me", headers=_auth_header(token))
    assert response.status_code == 200, response.text
    return response.json()


def _fund_account(account_id: str, amount: Decimal) -> None:
    db = SessionLocal()
    try:
        AccountRepository(db).increase_balance(uuid.UUID(account_id), amount)
        db.commit()
    finally:
        db.close()


def _create_payment_with_risk(
    client: TestClient,
    token: str,
    receiver_iban: str,
    amount: str,
    risk_level: RiskLevel,
) -> dict:
    original_evaluator = risk_service.RiskService.evaluate_transaction_risk
    risk_service.RiskService.evaluate_transaction_risk = staticmethod(
        _risk_evaluator_for(risk_level)
    )

    try:
        response = client.post(
            "/api/payments",
            json={
                "receiver_iban": receiver_iban,
                "amount": amount,
                "currency": "EUR",
                "description": f"integration {risk_level.value.lower()}",
            },
            headers=_auth_header(token),
        )
    finally:
        risk_service.RiskService.evaluate_transaction_risk = original_evaluator

    assert response.status_code == 201, response.text
    return response.json()


def _create_pending_payment(
    client: TestClient,
    token: str,
    receiver_iban: str,
    amount: str,
) -> dict:
    original_evaluator = risk_service.RiskService.evaluate_transaction_risk

    def unavailable_evaluator(**_kwargs):
        raise payment_service.PaymentDependencyNotReadyError("Risk unavailable.")

    risk_service.RiskService.evaluate_transaction_risk = staticmethod(
        unavailable_evaluator
    )

    try:
        response = client.post(
            "/api/payments",
            json={
                "receiver_iban": receiver_iban,
                "amount": amount,
                "currency": "EUR",
                "description": "integration pending",
            },
            headers=_auth_header(token),
        )
    finally:
        risk_service.RiskService.evaluate_transaction_risk = original_evaluator

    assert response.status_code == 201, response.text
    return response.json()


def _confirm_payment(
    client: TestClient,
    token: str,
    payment_id: str,
    password: str | None = None,
) -> dict:
    payload = {}
    if password is not None:
        payload["password"] = password

    response = client.post(
        f"/api/payments/{payment_id}/confirm",
        json=payload,
        headers=_auth_header(token),
    )
    assert response.status_code == 200, response.text
    return response.json()


def _cancel_payment(
    client: TestClient,
    token: str,
    payment_id: str,
) -> dict:
    response = client.post(
        f"/api/payments/{payment_id}/cancel",
        json={},
        headers=_auth_header(token),
    )
    assert response.status_code == 200, response.text
    return response.json()


def _risk_evaluator_for(risk_level: RiskLevel) -> Callable:
    def evaluator(
        db: Session,
        transaction_id: uuid.UUID,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        amount: Decimal,
        description: str | None,
        created_at,
    ):
        _ = sender_id, receiver_id, amount, description, created_at
        rule_score, anomaly_score, combined_score, decision = _scores_for(risk_level)
        return RiskAssessmentRepository(db).create_risk_assessment(
            transaction_id=transaction_id,
            rule_score=rule_score,
            anomaly_score=anomaly_score,
            combined_score=combined_score,
            risk_level=risk_level,
            decision=decision,
            evaluated_at=created_at,
        )

    return evaluator


def _scores_for(
    risk_level: RiskLevel,
) -> tuple[Decimal, Decimal, Decimal, RiskDecision]:
    if risk_level == RiskLevel.LOW:
        return (
            Decimal("0.100"),
            Decimal("0.100"),
            Decimal("0.100"),
            RiskDecision.ALLOW,
        )

    if risk_level == RiskLevel.MEDIUM:
        return (
            Decimal("0.500"),
            Decimal("0.500"),
            Decimal("0.500"),
            RiskDecision.WARN,
        )

    return (
        Decimal("0.900"),
        Decimal("0.900"),
        Decimal("0.900"),
        RiskDecision.REJECT,
    )


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_database_available() -> None:
    database_url = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
    try:
        with psycopg.connect(database_url, connect_timeout=3):
            return
    except psycopg.OperationalError as exc:
        raise RuntimeError(
            "Integration tests require the configured PostgreSQL database to be "
            "running and migrated with dev/02_tables.sql."
        ) from exc


if __name__ == "__main__":
    main()
