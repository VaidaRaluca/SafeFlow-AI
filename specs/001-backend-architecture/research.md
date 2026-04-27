# Research: FastAPI Backend Architecture Skeleton

## Decision 1: Use strict 4-layer backend flow
- Decision: Use `Controller/Router -> Service -> Repository -> Database` as the mandatory internal flow.
- Rationale: Matches the approved specification and keeps responsibilities explicit for a skeleton that will later receive implementation logic.
- Alternatives considered:
  - Router -> Repository (rejected: bypasses business layer and weakens future maintainability).
  - Service -> Database directly (rejected: removes data-access abstraction).

## Decision 2: Deliver skeleton-only artifacts
- Decision: Create only directory structure and placeholder files with short responsibility docstrings/comments.
- Rationale: User constraints explicitly prohibit business logic, endpoint implementations, SQL generation, and DB modifications.
- Alternatives considered:
  - Partial endpoint stubs (rejected: would drift toward implementation).
  - Sample service methods (rejected: introduces business logic prematurely).

## Decision 3: Preserve existing database as immutable integration boundary
- Decision: Map only to existing tables (`users`, `accounts`, `contacts`, `transactions`, `risk_assessments`) and existing enums (`currency_code`, `transaction_status`, `risk_level`, `risk_decision`).
- Rationale: Database is owned by another team member and must not be modified or redesigned.
- Alternatives considered:
  - Schema normalization proposal (rejected: out of scope and forbidden).
  - Migration scaffolding generation (rejected: implies DB change workflow).

## Decision 4: Treat API layer as ownership map, not implementation
- Decision: Define endpoint-to-file ownership contracts for the required endpoints without implementing handlers.
- Rationale: Supports architecture clarity and SC-001 while staying within non-implementation constraints.
- Alternatives considered:
  - Generate OpenAPI implementation-first contract (rejected: not needed for skeleton-only stage).

## Decision 5: Keep testing structure minimal and architecture-aligned
- Decision: Create `tests/unit` and `tests/integration` directories with placeholder test ownership notes only.
- Rationale: Ensures immediate test-layout alignment with the layered architecture while deferring test logic.
- Alternatives considered:
  - Add concrete tests now (rejected: implementation phase not started).
