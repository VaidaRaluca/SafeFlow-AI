CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    segment VARCHAR(100) NOT NULL,
    base_currency CHAR(3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status customer_status NOT NULL DEFAULT 'ACTIVE',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_customers_base_currency
        CHECK (base_currency ~ '^[A-Z]{3}$')
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    currency CHAR(3) NOT NULL,
	current_balance NUMERIC(18,2) NOT NULL DEFAULT 0.00,
    available_balance NUMERIC(18,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status account_status NOT NULL DEFAULT 'ACTIVE',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_accounts_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,

    CONSTRAINT chk_accounts_currency
        CHECK (currency ~ '^[A-Z]{3}$'),

    CONSTRAINT chk_accounts_balances_non_negative
        CHECK (current_balance >= 0 AND available_balance >= 0),

    CONSTRAINT chk_accounts_available_le_current
        CHECK (available_balance <= current_balance)
);

CREATE TABLE IF NOT EXISTS beneficiaries (
    beneficiary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    beneficiary_name VARCHAR(255) NOT NULL,
   	iban VARCHAR(64) NOT NULL,
    bank_code VARCHAR(32),
    beneficiary_type beneficiary_type_enum NOT NULL DEFAULT 'PERSON',
    is_saved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_beneficiaries_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,

    CONSTRAINT uq_beneficiaries_customer_iban
        UNIQUE (customer_id, iban)
);

CREATE TABLE IF NOT EXISTS device_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    device_fingerprint VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    city VARCHAR(120),
    country VARCHAR(120),
    user_agent TEXT,
    login_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_device_sessions_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    beneficiary_id UUID,
    session_id UUID NOT NULL,
    account_id UUID NOT NULL,

    amount NUMERIC(18,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    reference_text VARCHAR(255),
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    status payment_status NOT NULL DEFAULT 'PENDING_REVIEW',
    decision risk_decision,
    final_outcome final_outcome_type,
    executed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_payments_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,

    CONSTRAINT fk_payments_beneficiary
        FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id) ON DELETE SET NULL,

    CONSTRAINT fk_payments_session
        FOREIGN KEY (session_id) REFERENCES device_sessions(session_id) ON DELETE RESTRICT,

    CONSTRAINT fk_payments_account
        FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,

    CONSTRAINT chk_payments_amount_positive
        CHECK (amount > 0),

    CONSTRAINT chk_payments_currency
        CHECK (currency ~ '^[A-Z]{3}$')
);

CREATE TABLE IF NOT EXISTS payment_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL,
    event_type event_type_enum NOT NULL,
    old_status payment_status,
    new_status payment_status,
    actor_type actor_type_enum NOT NULL,
    actor_id VARCHAR(100),
    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT,

    CONSTRAINT fk_payment_events_payment
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL UNIQUE,
    rule_score NUMERIC(10,4) NOT NULL DEFAULT 0,
    anomaly_score NUMERIC(10,4) NOT NULL DEFAULT 0,
    decision risk_decision NOT NULL,
    reason_codes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_version VARCHAR(64),
    feature_snapshot_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    ground_truth_label VARCHAR(32),
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_risk_assessments_payment
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE,

    CONSTRAINT chk_risk_scores_non_negative
        CHECK (rule_score >= 0 AND anomaly_score >= 0)
);

CREATE TABLE IF NOT EXISTS analyst_cases (
    case_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL UNIQUE,
    case_status case_status_enum NOT NULL DEFAULT 'OPEN',
    assigned_to VARCHAR(255),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_analyst_cases_payment
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    ledger_entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    payment_id UUID NOT NULL,
    entry_type ledger_entry_type_enum NOT NULL,
    amount_delta NUMERIC(18,2) NOT NULL,
    balance_after NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ledger_entries_account
        FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,

    CONSTRAINT fk_ledger_entries_payment
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE
);