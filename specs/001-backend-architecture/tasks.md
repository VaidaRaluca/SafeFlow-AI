# Tasks: FastAPI Backend Architecture Skeleton

**Input**: Design documents from `/specs/001-backend-architecture/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No test implementation tasks are included. Scope is skeleton structure only.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2])
- Every task includes an exact path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the base directory structure needed for the backend skeleton.

- [ ] T001 Create root backend folder `app/`
- [ ] T002 [P] Create API routes folder `app/api/routes/`
- [ ] T003 [P] Create service layer folder `app/services/`
- [ ] T004 [P] Create repository layer folder `app/repositories/`
- [ ] T005 [P] Create model layer folder `app/models/`
- [ ] T006 [P] Create schema layer folder `app/schemas/`
- [ ] T007 [P] Create database folder `app/db/`
- [ ] T008 [P] Create core utilities folder `app/core/`
- [ ] T009 [P] Create dependencies folder `app/dependencies/`
- [ ] T010 [P] Create unit test folder `tests/unit/`
- [ ] T011 [P] Create integration test folder `tests/integration/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create foundational placeholder files shared by all stories.

**⚠️ CRITICAL**: No user story work should start before this phase is complete.

- [ ] T012 Create DB session placeholder file with one short responsibility comment in `app/db/session.py`
- [ ] T013 Create DB base placeholder file with one short responsibility comment in `app/db/base.py`
- [ ] T014 Create configuration placeholder file with one short responsibility comment in `app/core/config.py`
- [ ] T015 Create exceptions placeholder file with one short responsibility comment in `app/core/exceptions.py`
- [ ] T016 Create database dependency placeholder file with one short responsibility comment in `app/dependencies/database.py`

**Checkpoint**: Foundation ready for story-specific skeleton creation.

---

## Phase 3: User Story 1 - Authentication Skeleton Ownership (Priority: P1) 🎯 MVP

**Goal**: Establish auth-layer file placement across router, service, repository, model, schema, and security/dependency modules.

**Independent Test**: A developer can locate all auth-related placeholders and confirm each has exactly one short responsibility comment with no implementation logic.

- [ ] T017 [P] [US1] Create auth route placeholder file with one short responsibility comment in `app/api/routes/auth.py`
- [ ] T018 [P] [US1] Create auth service placeholder file with one short responsibility comment in `app/services/auth_service.py`
- [ ] T019 [P] [US1] Create user repository placeholder file with one short responsibility comment in `app/repositories/user_repository.py`
- [ ] T020 [P] [US1] Create user model placeholder file with one short responsibility comment in `app/models/user.py`
- [ ] T021 [P] [US1] Create auth schema placeholder file with one short responsibility comment in `app/schemas/auth.py`
- [ ] T022 [P] [US1] Create auth dependency placeholder file with one short responsibility comment in `app/dependencies/auth.py`
- [ ] T023 [P] [US1] Create security placeholder file with one short responsibility comment in `app/core/security.py`

**Checkpoint**: Auth skeleton structure is complete and independently reviewable.

---

## Phase 4: User Story 2 - Account and Onboarding Structure (Priority: P1)

**Goal**: Add account-focused placeholders and onboarding-relevant API structure without implementing behavior.

**Independent Test**: A new developer can find account API/service/repository/model/schema placeholders and understand responsibilities from single-line comments.

- [ ] T024 [P] [US2] Create accounts route placeholder file with one short responsibility comment in `app/api/routes/accounts.py`
- [ ] T025 [P] [US2] Create account service placeholder file with one short responsibility comment in `app/services/account_service.py`
- [ ] T026 [P] [US2] Create account repository placeholder file with one short responsibility comment in `app/repositories/account_repository.py`
- [ ] T027 [P] [US2] Create account model placeholder file with one short responsibility comment in `app/models/account.py`
- [ ] T028 [P] [US2] Create account schema placeholder file with one short responsibility comment in `app/schemas/account.py`

**Checkpoint**: Account skeleton structure is complete and independently reviewable.

---

## Phase 5: User Story 3 - Database Table Mapping Skeleton (Priority: P1)

**Goal**: Create placeholders that map all remaining existing tables/enums to model and repository modules.

**Independent Test**: A developer can map `contacts`, `transactions`, and `risk_assessments` to matching model and repository placeholders, and locate enum placeholders.

- [ ] T029 [P] [US3] Create contact repository placeholder file with one short responsibility comment in `app/repositories/contact_repository.py`
- [ ] T030 [P] [US3] Create transaction repository placeholder file with one short responsibility comment in `app/repositories/transaction_repository.py`
- [ ] T031 [P] [US3] Create risk assessment repository placeholder file with one short responsibility comment in `app/repositories/risk_assessment_repository.py`
- [ ] T032 [P] [US3] Create contact model placeholder file with one short responsibility comment in `app/models/contact.py`
- [ ] T033 [P] [US3] Create transaction model placeholder file with one short responsibility comment in `app/models/transaction.py`
- [ ] T034 [P] [US3] Create risk assessment model placeholder file with one short responsibility comment in `app/models/risk_assessment.py`
- [ ] T035 [P] [US3] Create enum mapping placeholder file with one short responsibility comment in `app/models/enums.py`
- [ ] T036 [P] [US3] Create user schema placeholder file with one short responsibility comment in `app/schemas/user.py`

**Checkpoint**: Existing DB table and enum skeleton mapping is complete and independently reviewable.

---

## Phase 6: User Story 4 - Endpoint Mapping Skeleton (Priority: P2)

**Goal**: Create placeholders for payments/transactions endpoints and supporting services/schemas.

**Independent Test**: A developer can trace required payment/transaction endpoints to router/service/repository ownership files without implementation code.

- [ ] T037 [P] [US4] Create payments route placeholder file with one short responsibility comment in `app/api/routes/payments.py`
- [ ] T038 [P] [US4] Create transactions route placeholder file with one short responsibility comment in `app/api/routes/transactions.py`
- [ ] T039 [P] [US4] Create payment service placeholder file with one short responsibility comment in `app/services/payment_service.py`
- [ ] T040 [P] [US4] Create transaction service placeholder file with one short responsibility comment in `app/services/transaction_service.py`
- [ ] T041 [P] [US4] Create risk service placeholder file with one short responsibility comment in `app/services/risk_service.py`
- [ ] T042 [P] [US4] Create rule score service placeholder file with one short responsibility comment in `app/services/rule_score_service.py`
- [ ] T043 [P] [US4] Create anomaly score service placeholder file with one short responsibility comment in `app/services/anomaly_score_service.py`
- [ ] T044 [P] [US4] Create settlement service placeholder file with one short responsibility comment in `app/services/settlement_service.py`
- [ ] T045 [P] [US4] Create payment schema placeholder file with one short responsibility comment in `app/schemas/payment.py`
- [ ] T046 [P] [US4] Create transaction schema placeholder file with one short responsibility comment in `app/schemas/transaction.py`
- [ ] T047 [P] [US4] Create risk schema placeholder file with one short responsibility comment in `app/schemas/risk.py`

**Checkpoint**: Endpoint-to-layer skeleton ownership is complete and independently reviewable.

---

## Phase 7: User Story 5 - Layer Responsibility Clarity (Priority: P2)

**Goal**: Enforce one-line layer ownership clarity in representative files so boundaries are explicit.

**Independent Test**: Reviewers can open the representative files and verify comments clearly state router/service/repository/model/schema responsibilities and contain no implementation logic.

- [ ] T048 [US5] Refine placeholder comment to explicitly state thin-router responsibility in `app/api/routes/auth.py`
- [ ] T049 [US5] Refine placeholder comment to explicitly state business-orchestration responsibility in `app/services/payment_service.py`
- [ ] T050 [US5] Refine placeholder comment to explicitly state query-only responsibility in `app/repositories/transaction_repository.py`
- [ ] T051 [US5] Refine placeholder comment to explicitly state table-mapping responsibility in `app/models/transaction.py`
- [ ] T052 [US5] Refine placeholder comment to explicitly state DTO-only responsibility in `app/schemas/transaction.py`

**Checkpoint**: Layer boundary messaging is explicit and consistent.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final structure validation against SC-001 with no implementation logic introduced.

- [ ] T053 Validate required folder tree exists according to `specs/001-backend-architecture/plan.md`
- [ ] T054 Validate all required placeholder files exist according to `specs/001-backend-architecture/quickstart.md`
- [ ] T055 Validate each placeholder file contains at most one short responsibility comment/docstring according to `specs/001-backend-architecture/contracts/backend-skeleton-contract.md`
- [ ] T056 Validate no business logic, endpoint implementation, SQL, or DB changes are present in `app/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user stories.
- **US1-US4 (Phases 3-6)**: Depend on Phase 2 completion.
- **US5 (Phase 7)**: Depends on representative files from US1-US4.
- **Polish (Phase 8)**: Depends on all prior phases.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; MVP entry point.
- **US2 (P1)**: Starts after Foundational; independent from US1 implementation details.
- **US3 (P1)**: Starts after Foundational; independent from US1/US2 implementation details.
- **US4 (P2)**: Starts after Foundational; can run in parallel with US2/US3.
- **US5 (P2)**: Requires representative files from US1-US4 to exist.

### Within Each User Story

- Create placeholder files first.
- Add or refine one short responsibility comment/docstring per file.
- Do not add any implementation logic.

### Parallel Opportunities

- All tasks marked [P] can run in parallel within their phase.
- After Phase 2, US1-US4 can be staffed in parallel.

---

## Parallel Example: User Story 4

```bash
# Parallel file creation for US4 route placeholders:
Task: T037 app/api/routes/payments.py
Task: T038 app/api/routes/transactions.py

# Parallel file creation for US4 service placeholders:
Task: T039 app/services/payment_service.py
Task: T040 app/services/transaction_service.py
Task: T041 app/services/risk_service.py
Task: T042 app/services/rule_score_service.py
Task: T043 app/services/anomaly_score_service.py
Task: T044 app/services/settlement_service.py
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 placeholders for scope compliance.

### Incremental Delivery

1. Foundation complete (Phases 1-2).
2. Deliver US1, then US2/US3, then US4.
3. Apply US5 boundary-clarity refinements.
4. Run final validation in Phase 8.

### Parallel Team Strategy

1. Team completes Phases 1-2 together.
2. Split US1-US4 across developers in parallel.
3. Consolidate with US5 and Phase 8 validation.

---

## Notes

- Task scope is intentionally limited to structure and placeholders.
- No tasks include business logic, endpoint implementation, SQL, schema changes, or auth logic implementation.
- SC-001 is the completion gate for this tasks file.
