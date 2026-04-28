-- 02_tables.sql
-- SafeFlow AI - PostgreSQL tables
-- Rulează după 01_setup.sql.

BEGIN;

DROP TABLE IF EXISTS risk_assessments CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    iban VARCHAR(34) NOT NULL UNIQUE,
    balance NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    currency currency_code NOT NULL DEFAULT 'EUR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT accounts_balance_non_negative CHECK (balance >= 0),
    CONSTRAINT accounts_iban_length CHECK (char_length(iban) BETWEEN 15 AND 34)
);

CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_trusted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT contacts_no_self_contact CHECK (sender_id <> receiver_id),
    CONSTRAINT contacts_unique_sender_receiver UNIQUE (sender_id, receiver_id)
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    receiver_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    amount NUMERIC(14, 2) NOT NULL,
    currency currency_code NOT NULL DEFAULT 'EUR',
    description TEXT NULL,
    status transaction_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    confirmed_at TIMESTAMPTZ NULL,
    settled_at TIMESTAMPTZ NULL,
    requires_password_confirmation BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT transactions_positive_amount CHECK (amount > 0),
    CONSTRAINT transactions_no_self_transfer CHECK (sender_id <> receiver_id),
    CONSTRAINT transactions_confirmed_after_created CHECK (
        confirmed_at IS NULL OR confirmed_at >= created_at
    ),
    CONSTRAINT transactions_settled_after_created CHECK (
        settled_at IS NULL OR settled_at >= created_at
    ),
    CONSTRAINT transactions_confirmed_equals_settled CHECK (
        confirmed_at IS NULL OR settled_at IS NULL OR confirmed_at = settled_at
    )
);

CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
    rule_score NUMERIC(4, 3) NOT NULL,
    anomaly_score NUMERIC(4, 3) NOT NULL,
    combined_score NUMERIC(4, 3) NOT NULL,
    risk_level risk_level NOT NULL,
    decision risk_decision NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT risk_rule_score_range CHECK (rule_score >= 0 AND rule_score <= 1),
    CONSTRAINT risk_anomaly_score_range CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    CONSTRAINT risk_combined_score_range CHECK (combined_score >= 0 AND combined_score <= 2),
    CONSTRAINT risk_level_decision_consistency CHECK (
        (risk_level = 'LOW' AND decision = 'ALLOW')
        OR (risk_level = 'MEDIUM' AND decision = 'WARN')
        OR (risk_level = 'HIGH' AND decision = 'REJECT')
    )
);

-- updated_at trigger reutilizabil pentru tabelele care au coloana updated_at.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_accounts_updated_at
BEFORE UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Indecși pentru endpoint-uri și calcule de risk score.
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_contacts_sender_receiver ON contacts(sender_id, receiver_id);
CREATE INDEX IF NOT EXISTS idx_transactions_sender_created_at ON transactions(sender_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_receiver_created_at ON transactions(receiver_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_sender_receiver ON transactions(sender_id, receiver_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_transaction_id ON risk_assessments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_risk_level ON risk_assessments(risk_level);

COMMIT;
