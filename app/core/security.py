import base64
import binascii
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings


PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class TokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()

    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations, salt, stored_digest = password_hash.split("$", 3)
        iteration_count = int(iterations)
    except ValueError:
        return False

    if scheme != PASSWORD_SCHEME:
        return False

    candidate_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iteration_count,
    ).hex()

    return hmac.compare_digest(candidate_digest, stored_digest)


def create_access_token(subject: str) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject=subject, token_type=ACCESS_TOKEN_TYPE, expires_delta=expires_delta)


def create_refresh_token(subject: str) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject=subject, token_type=REFRESH_TOKEN_TYPE, expires_delta=expires_delta)


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise TokenError("Invalid token format.") from exc

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    expected_signature = _sign(signing_input)

    try:
        signature = _base64url_decode(encoded_signature)
    except (binascii.Error, ValueError) as exc:
        raise TokenError("Invalid token signature.") from exc

    if not hmac.compare_digest(signature, expected_signature):
        raise TokenError("Invalid token signature.")

    try:
        header = json.loads(_base64url_decode(encoded_header))
        payload = json.loads(_base64url_decode(encoded_payload))
    except (binascii.Error, ValueError, json.JSONDecodeError) as exc:
        raise TokenError("Invalid token payload.") from exc

    if header.get("alg") != settings.ALGORITHM or header.get("typ") != "JWT":
        raise TokenError("Unsupported token header.")

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        raise TokenError("Token expiration is missing.")

    if expires_at < int(datetime.now(UTC).timestamp()):
        raise TokenError("Token expired.")

    token_type = payload.get("type")
    if expected_type is not None and token_type != expected_type:
        raise TokenError("Unexpected token type.")

    return payload


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    if settings.ALGORITHM != "HS256":
        raise TokenError("Only HS256 tokens are supported.")

    now = datetime.now(UTC)
    header = {
        "alg": settings.ALGORITHM,
        "typ": "JWT",
    }
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }

    encoded_header = _base64url_encode(_json_bytes(header))
    encoded_payload = _base64url_encode(_json_bytes(payload))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    encoded_signature = _base64url_encode(_sign(signing_input))

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def _json_bytes(data: dict[str, Any]) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _sign(signing_input: bytes) -> bytes:
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)
