# Data Model: Backend Skeleton Mapping (No Schema Changes)

## Scope
This artifact maps existing PostgreSQL tables to backend model and repository placeholders only. No SQL, migration, or schema redesign is included.

## Entities and File Ownership

### User
- Existing table: `users`
- Model placeholder: `app/models/user.py`
- Repository placeholder: `app/repositories/user_repository.py`
- Related services: `app/services/auth_service.py`, `app/services/account_service.py`
- Purpose in skeleton: authentication identity and account ownership reference.

### Account
- Existing table: `accounts`
- Model placeholder: `app/models/account.py`
- Repository placeholder: `app/repositories/account_repository.py`
- Related services: `app/services/account_service.py`, `app/services/settlement_service.py`
- Purpose in skeleton: balance and account state boundary.

### Contact
- Existing table: `contacts`
- Model placeholder: `app/models/contact.py`
- Repository placeholder: `app/repositories/contact_repository.py`
- Related services: `app/services/payment_service.py`, `app/services/risk_service.py`
- Purpose in skeleton: beneficiary/trust relationship ownership.

### Transaction
- Existing table: `transactions`
- Model placeholder: `app/models/transaction.py`
- Repository placeholder: `app/repositories/transaction_repository.py`
- Related services: `app/services/payment_service.py`, `app/services/transaction_service.py`, `app/services/settlement_service.py`
- Purpose in skeleton: lifecycle state tracking (`PENDING`, `APPROVED`, `WARNED`, `SETTLED`, `CANCELED`, `REJECTED`).

### RiskAssessment
- Existing table: `risk_assessments`
- Model placeholder: `app/models/risk_assessment.py`
- Repository placeholder: `app/repositories/risk_assessment_repository.py`
- Related services: `app/services/risk_service.py`, `app/services/rule_score_service.py`, `app/services/anomaly_score_service.py`
- Purpose in skeleton: risk evaluation record ownership per transaction.

## Enum Mapping
- Existing DB enums mapped in placeholder: `app/models/enums.py`
- Enum set:
  - `currency_code`: `EUR`, `RON`, `USD`, `GBP`
  - `transaction_status`: `PENDING`, `APPROVED`, `WARNED`, `SETTLED`, `CANCELED`, `REJECTED`
  - `risk_level`: `LOW`, `MEDIUM`, `HIGH`
  - `risk_decision`: `ALLOW`, `WARN`, `REJECT`

## Relationships (Architecture-Level)
- User -> Account: one-to-many ownership boundary (implementation deferred).
- User/Account -> Contact: sender-beneficiary relationship boundary.
- Transaction -> RiskAssessment: one risk assessment record per transaction as a business invariant (implementation deferred).
- Transaction -> Account: settlement impact boundary for balance updates (implementation deferred).

## Validation Constraints for Skeleton Phase
- Keep model placeholders aligned to existing table names only.
- Do not add new entities, tables, or enum values.
- Defer all relation mechanics and constraints to implementation phase.
