# Quickstart: Build the Backend Skeleton Only

## Goal
Create only the FastAPI backend architecture skeleton from the approved specification so SC-001 is satisfied.

## Scope Rules (Mandatory)
- Create folders and placeholder files only.
- Do not add business logic.
- Do not implement endpoints.
- Do not add SQL.
- Do not modify the existing database.
- Each placeholder file should contain only a short responsibility comment/docstring.

## Required Directory Tree

```text
app/
  api/routes/
  services/
  repositories/
  models/
  schemas/
  db/
  core/
  dependencies/
tests/
  unit/
  integration/
```

## Required Placeholder Files

### Routes
- `app/api/routes/auth.py`
- `app/api/routes/accounts.py`
- `app/api/routes/payments.py`
- `app/api/routes/transactions.py`

### Services
- `app/services/auth_service.py`
- `app/services/account_service.py`
- `app/services/payment_service.py`
- `app/services/transaction_service.py`
- `app/services/risk_service.py`
- `app/services/rule_score_service.py`
- `app/services/anomaly_score_service.py`
- `app/services/settlement_service.py`

### Repositories
- `app/repositories/user_repository.py`
- `app/repositories/account_repository.py`
- `app/repositories/contact_repository.py`
- `app/repositories/transaction_repository.py`
- `app/repositories/risk_assessment_repository.py`

### Models
- `app/models/user.py`
- `app/models/account.py`
- `app/models/contact.py`
- `app/models/transaction.py`
- `app/models/risk_assessment.py`
- `app/models/enums.py`

### Schemas
- `app/schemas/auth.py`
- `app/schemas/user.py`
- `app/schemas/account.py`
- `app/schemas/payment.py`
- `app/schemas/transaction.py`
- `app/schemas/risk.py`

### Database Layer
- `app/db/session.py`
- `app/db/base.py`

### Core
- `app/core/config.py`
- `app/core/security.py`
- `app/core/exceptions.py`

### Dependencies
- `app/dependencies/auth.py`
- `app/dependencies/database.py`

## Placeholder Content Rule
Each file should include one short description of responsibility only. Example pattern:
- route file: "Defines auth HTTP route ownership only (no implementation)."
- service file: "Defines payment business orchestration ownership only (no implementation)."
- repository file: "Defines transaction data-access ownership only (no implementation)."

## Completion Checklist
- All listed folders exist.
- All listed files exist.
- No file includes business logic.
- No file includes endpoint implementation code.
- No file includes SQL.
- Existing database artifacts remain untouched.

## Outcome
When all checks pass, backend skeleton structure is ready for the next phase and SC-001 is satisfied.
