# Feature Specification: FastAPI Backend Architecture

**Feature Branch**: `001-backend-architecture`  
**Created**: 2026-04-27  
**Status**: Draft  
**Input**: Define backend folder structure, layer responsibilities, and file organization for SafeFlow AI payment processor demo system

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Implements Auth Feature (Priority: P1)

A developer needs to add the registration endpoint. They should be able to locate the router, service, and repository files without confusion, understand which code goes where, and follow the established layering pattern.

**Why this priority**: This is the foundation for all subsequent backend work. If the architecture is clear and consistent, all other features follow the same pattern, accelerating development.

**Independent Test**: A developer can implement the `/auth/register` endpoint following the documented architecture pattern, with clear separation between HTTP handling, business logic, and database access.

**Acceptance Scenarios**:

1. **Given** a developer opening the project, **When** they navigate to `app/api/routes/`, **Then** they find `auth.py` and understand it contains endpoint definitions only
2. **Given** a developer in `auth.py`, **When** they need business logic, **Then** they navigate to `app/services/auth_service.py` and find the business logic there
3. **Given** a developer in `auth_service.py`, **When** they need database access, **Then** they navigate to `app/repositories/user_repository.py` and find query methods
4. **Given** a developer reading the directory structure, **When** they search for where to add password hashing, **Then** they correctly identify `app/core/security.py` as the appropriate location

---

### User Story 2 - Architecture Review and Onboarding (Priority: P1)

A new team member joins the project and needs to understand the overall backend architecture, how layers interact, and where each type of code belongs without reading code comments.

**Why this priority**: Clear architecture documentation supports team onboarding, reduces bugs, and ensures consistency across the codebase. This is equally important as the first story for long-term maintainability.

**Independent Test**: A new developer can read the architecture specification document, understand the layer responsibilities, view the folder structure, and successfully navigate to the correct files for different coding tasks.

**Acceptance Scenarios**:

1. **Given** the architecture specification, **When** a developer reads it, **Then** they understand the 4-layer pattern: Router → Service → Repository → Database
2. **Given** the folder structure documentation, **When** a developer needs to add error handling, **Then** they correctly identify `app/core/exceptions.py`
3. **Given** the requirements documentation, **When** a developer needs to implement JWT token handling, **Then** they correctly identify `app/core/security.py` and `app/dependencies/auth.py`
4. **Given** the mapping documentation, **When** a developer looks up the `/api/payments/{id}/confirm` endpoint, **Then** they find it maps to `payments.py` router, `payment_service.py` service, and `transaction_repository.py` repository

---

### User Story 3 - Map Database Tables to Models and Services (Priority: P1)

A developer needs to understand which database tables exist, which ORM models represent them, and which services provide business logic for them, without reading code.

**Why this priority**: Clear mapping prevents confusion, reduces bugs from using wrong models, and ensures the team doesn't duplicate database access logic or miss tables.

**Independent Test**: The specification includes a clear mapping showing: database table → ORM model file → corresponding repository file → corresponding service files. A developer can look up any table and find all related code files.

**Acceptance Scenarios**:

1. **Given** the table-to-model mapping, **When** a developer needs to work with users, **Then** they find `users` table maps to `app/models/user.py`
2. **Given** the database schema, **When** a developer asks "which repository handles transactions?", **Then** they find `app/repositories/transaction_repository.py` and `app/models/transaction.py`
3. **Given** the service mapping, **When** a developer needs payment logic, **Then** they find it in `app/services/payment_service.py` and understand which repository methods it uses
4. **Given** a developer implementing risk assessment, **When** they look for the model, **Then** they find `app/models/risk_assessment.py` and `app/repositories/risk_assessment_repository.py`

---

### User Story 4 - Endpoint-to-Code Mapping for Testing/Debugging (Priority: P2)

A QA engineer or developer needs to trace a specific API endpoint through the codebase to understand what happens when that endpoint is called, which services are invoked, and which database operations occur.

**Why this priority**: When debugging issues or writing tests, engineers need to quickly locate all code involved in an endpoint's request flow. This reduces debugging time and improves test coverage.

**Independent Test**: The specification includes a complete mapping of all required endpoints to their router, service, and repository files. An engineer can look up any endpoint and trace it through all layers.

**Acceptance Scenarios**:

1. **Given** the endpoint mapping, **When** debugging `POST /auth/login`, **Then** they find it in `auth.py` router, `auth_service.py` service, and `user_repository.py` repository
2. **Given** the endpoint mapping, **When** investigating `POST /api/payments`, **Then** they understand it involves `payment_service.py`, `transaction_repository.py`, and multiple other services (risk, rule score, anomaly score)
3. **Given** a failing test for `GET /api/transactions/{id}`, **When** they look up the mapping, **Then** they find the transaction details flow through `transactions.py` router and `transaction_service.py` service
4. **Given** the endpoint mapping, **When** implementing integration tests, **Then** they understand all the layers involved in each endpoint

---

### User Story 5 - Layer Responsibility Clarity (Priority: P2)

A developer is uncertain whether logic belongs in a router, service, or repository. They should be able to quickly reference the architecture specification to understand layer responsibilities.

**Why this priority**: Consistent layer separation prevents "god objects" and makes code easier to test, maintain, and refactor. This reduces technical debt accumulation over time.

**Independent Test**: The specification includes a clear description of what code belongs in each layer. A developer can read the responsibility descriptions and correctly decide where to place new code.

**Acceptance Scenarios**:

1. **Given** the responsibility definitions, **When** a developer asks "where does password validation belong?", **Then** they correctly identify `app/core/security.py` (cross-layer utility) or the service layer (business logic)
2. **Given** the responsibility definitions, **When** a developer asks "where does SQL query construction belong?", **Then** they correctly identify the repository layer
3. **Given** the responsibility definitions, **When** a developer asks "where does HTTP status code mapping belong?", **Then** they correctly identify the router/controller layer
4. **Given** the responsibility definitions, **When** a developer asks "where does transaction status logic belong?", **Then** they correctly identify the service layer

---

### Edge Cases

- What happens when a feature needs to span multiple services? (e.g., payment confirmation requires transaction service, settlement service, and account service interaction)
- How are cross-cutting concerns handled? (e.g., logging, error handling, transaction rollback)
- Where does dependency injection configuration live?
- How are database sessions managed across the request lifecycle?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Backend MUST be organized in a 4-layer architecture: Router/Controller → Service → Repository → Database
- **FR-002**: Backend MUST have a dedicated `app/api/routes/` folder containing endpoint definitions for auth, accounts, payments, and transactions
- **FR-003**: Backend MUST have a dedicated `app/services/` folder containing business logic services for authentication, accounts, payments, transactions, risk assessment, rule scoring, anomaly scoring, and settlement
- **FR-004**: Backend MUST have a dedicated `app/repositories/` folder containing database query methods for each entity (users, accounts, contacts, transactions, risk_assessments)
- **FR-005**: Backend MUST have a dedicated `app/models/` folder containing ORM model definitions mapping to existing database tables
- **FR-006**: Backend MUST have a dedicated `app/schemas/` folder containing request/response DTO definitions separate from ORM models
- **FR-007**: Backend MUST have a dedicated `app/core/` folder containing cross-layer utilities: configuration, security, exception definitions, and middleware
- **FR-008**: Backend MUST have a dedicated `app/dependencies/` folder containing dependency injection utilities (database session management, JWT authentication)
- **FR-009**: Backend MUST have a dedicated `app/db/` folder containing database connection and session management code
- **FR-010**: Backend MUST have structured test folders: `tests/unit/` and `tests/integration/` maintaining the same layer organization as `app/`
- **FR-011**: Each router file MUST be thin and only expose API endpoints, delegating all business logic to services
- **FR-012**: Each service file MUST contain business logic and orchestration, using repositories for all database access
- **FR-013**: Each repository file MUST contain only database query methods, with no business logic
- **FR-014**: Each ORM model file MUST map to exactly one database table without modification to existing schema
- **FR-015**: Each schema file MUST define request and response DTOs, completely separate from ORM models
- **FR-016**: All API endpoints listed in requirements MUST map to specific router, service, and repository files
- **FR-017**: Backend MUST include service files for specialized features: risk assessment, rule scoring, anomaly score integration, and settlement logic
- **FR-018**: Backend MUST use PostgreSQL enums (currency_code, transaction_status, risk_level, risk_decision) mapped in models

### Key Entities *(include if feature involves data)*

- **User**: Represents registered users with credentials. Mapped to `users` table. Handled by `user.py` model, `user_repository.py` for DB access, and `auth_service.py`, `account_service.py` for business logic
- **Account**: Represents user accounts with balances and currency. Mapped to `accounts` table. Handled by `account.py` model, `account_repository.py`, and `account_service.py`
- **Contact**: Represents trusted/untrusted contacts. Mapped to `contacts` table. Handled by `contact.py` model, `contact_repository.py`
- **Transaction**: Represents payment transactions with status tracking. Mapped to `transactions` table. Handled by `transaction.py` model, `transaction_repository.py`, and `payment_service.py`, `transaction_service.py`, `settlement_service.py`
- **RiskAssessment**: Represents risk analysis results for transactions. Mapped to `risk_assessments` table. Handled by `risk_assessment.py` model, `risk_assessment_repository.py`, and `risk_service.py`, `rule_score_service.py`, `anomaly_score_service.py`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The backend folder structure is created exactly as specified in the architecture document, with all required folders and placeholder files
- **SC-002**: The architecture documentation includes clear, unambiguous descriptions of each layer's responsibilities, such that a developer can correctly place new code on first attempt 80% of the time without asking for clarification
- **SC-003**: A complete mapping exists showing all 10 required API endpoints mapped to their corresponding router file, service file, and repository file
- **SC-004**: A complete mapping exists showing all 5 database tables mapped to their corresponding ORM model files and repository files
- **SC-005**: The specification includes a request flow diagram showing how a single HTTP request flows through all 4 layers from Router → Service → Repository → Database → back to Router
- **SC-006**: New developers can use the architecture specification to navigate the codebase and locate appropriate files for implementing new features without code review or mentoring

## Assumptions

- The database schema (users, accounts, contacts, transactions, risk_assessments tables) is already implemented and will NOT be modified during architecture design
- FastAPI will be used as the web framework (standard for this project type)
- PostgreSQL will remain the database (as per existing schema)
- SQLAlchemy ORM will be used for database access (standard Python ORM choice)
- Pydantic will be used for request/response validation (FastAPI standard)
- PyJWT or similar will be used for JWT token handling
- A testing framework like pytest will be used for unit and integration tests
- The backend will use dependency injection for managing database sessions and authentication across the request lifecycle
- Error handling will be centralized in `app/core/exceptions.py` with appropriate HTTP status code mapping in routers
- Authentication (JWT tokens) will be managed through `app/core/security.py` and injected via `app/dependencies/auth.py`
- The settlement and balance update logic is part of the business layer, not directly tied to transaction confirmation
- Risk scoring involves multiple algorithms (rule score, anomaly score) coordinated by a risk service
- All endpoints return appropriate HTTP status codes and standardized error responses
