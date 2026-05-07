from enum import Enum


class CurrencyCode(str, Enum):
    EUR = "EUR"
    RON = "RON"
    USD = "USD"
    GBP = "GBP"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    WARNED = "WARNED"
    SETTLED = "SETTLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskDecision(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REJECT = "REJECT"
