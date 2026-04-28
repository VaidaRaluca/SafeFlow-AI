# Contract: Backend Skeleton Ownership and Layer Boundaries

## Purpose
Define ownership contracts for routes, services, repositories, models, schemas, and support modules for the backend skeleton. This is a structure contract, not an implementation contract.

## Layer Contract
- Routers (`app/api/routes/*.py`): expose HTTP endpoints only; delegate to services.
- Services (`app/services/*.py`): own business orchestration and rule flow; call repositories and specialized services.
- Repositories (`app/repositories/*.py`): own database access/query operations only.
- Models (`app/models/*.py`): map existing DB tables/enums only.
- Schemas (`app/schemas/*.py`): request/response DTO ownership only.
- DB layer (`app/db/*.py`): database session/base ownership only.

## Endpoint Ownership Contract

### Auth Endpoints
- `POST /auth/register`
  - Router: `app/api/routes/auth.py`
  - Service: `app/services/auth_service.py`
  - Repository: `app/repositories/user_repository.py`
- `POST /auth/login`
  - Router: `app/api/routes/auth.py`
  - Service: `app/services/auth_service.py`
  - Repository: `app/repositories/user_repository.py`
- `POST /auth/logout`
  - Router: `app/api/routes/auth.py`
  - Service: `app/services/auth_service.py`
  - Repository: `app/repositories/user_repository.py`
- `POST /auth/refresh`
  - Router: `app/api/routes/auth.py`
  - Service: `app/services/auth_service.py`
  - Repository: `app/repositories/user_repository.py`

### Account Endpoint
- `GET /api/accounts/me`
  - Router: `app/api/routes/accounts.py`
  - Service: `app/services/account_service.py`
  - Repository: `app/repositories/account_repository.py`

### Payment Endpoints
- `POST /api/payments`
  - Router: `app/api/routes/payments.py`
  - Service: `app/services/payment_service.py`
  - Repositories: `app/repositories/transaction_repository.py`, `app/repositories/contact_repository.py`, `app/repositories/risk_assessment_repository.py`
  - Supporting services: `app/services/risk_service.py`, `app/services/rule_score_service.py`, `app/services/anomaly_score_service.py`
- `POST /api/payments/{id}/confirm`
  - Router: `app/api/routes/payments.py`
  - Services: `app/services/payment_service.py`, `app/services/settlement_service.py`
  - Repositories: `app/repositories/transaction_repository.py`, `app/repositories/account_repository.py`
- `POST /api/payments/{id}/cancel`
  - Router: `app/api/routes/payments.py`
  - Service: `app/services/payment_service.py`
  - Repository: `app/repositories/transaction_repository.py`

### Transaction Endpoints
- `GET /api/transactions/me`
  - Router: `app/api/routes/transactions.py`
  - Service: `app/services/transaction_service.py`
  - Repository: `app/repositories/transaction_repository.py`
- `GET /api/transactions/{id}`
  - Router: `app/api/routes/transactions.py`
  - Service: `app/services/transaction_service.py`
  - Repository: `app/repositories/transaction_repository.py`

## Module Responsibility Contract (Placeholder Scope)
- Each file created for this skeleton contains only a short responsibility comment/docstring.
- No endpoint handler logic, no business rule code, and no SQL content in this phase.
- No database schema changes, migrations, or redesign artifacts in this phase.

## Validation Contract (SC-001)
The implementation is considered compliant when:
- all required folders exist,
- all required placeholder files exist,
- each placeholder file contains only responsibility-level text,
- no implementation logic is introduced.
