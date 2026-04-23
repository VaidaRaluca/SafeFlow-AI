-- =========================================================
-- Indexes
-- =========================================================

-- -------------------------
-- customers
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_customers_status
    ON customers(status);

CREATE INDEX IF NOT EXISTS idx_customers_created_at
    ON customers(created_at DESC);

-- -------------------------
-- accounts
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
    ON accounts(customer_id);

CREATE INDEX IF NOT EXISTS idx_accounts_status
    ON accounts(status);

CREATE INDEX IF NOT EXISTS idx_accounts_currency5
    ON accounts(currency);

-- -------------------------
-- beneficiaries
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_beneficiaries_customer_id
    ON beneficiaries(customer_id);

CREATE INDEX IF NOT EXISTS idx_beneficiaries_created_at
    ON beneficiaries(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_beneficiaries_is_saved
    ON beneficiaries(is_saved);

CREATE INDEX IF NOT EXISTS idx_beneficiaries_customer_created_at
    ON beneficiaries(customer_id, created_at DESC);

-- -------------------------
-- device_sessions
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_device_sessions_customer_id
    ON device_sessions(customer_id);

CREATE INDEX IF NOT EXISTS idx_device_sessions_device_fingerprint
    ON device_sessions(device_fingerprint);

CREATE INDEX IF NOT EXISTS idx_device_sessions_customer_fingerprint
    ON device_sessions(customer_id, device_fingerprint);

CREATE INDEX IF NOT EXISTS idx_device_sessions_last_seen_at
    ON device_sessions(last_seen_at DESC);

CREATE INDEX IF NOT EXISTS idx_device_sessions_customer_last_seen
    ON device_sessions(customer_id, last_seen_at DESC);

CREATE INDEX IF NOT EXISTS idx_device_sessions_customer_location
    ON device_sessions(customer_id, country, city);

-- -------------------------
-- payments
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_payments_customer_id
    ON payments(customer_id);

CREATE INDEX IF NOT EXISTS idx_payments_account_id
    ON payments(account_id);

CREATE INDEX IF NOT EXISTS idx_payments_beneficiary_id
    ON payments(beneficiary_id);

CREATE INDEX IF NOT EXISTS idx_payments_session_id
    ON payments(session_id);

CREATE INDEX IF NOT EXISTS idx_payments_status
    ON payments(status);

CREATE INDEX IF NOT EXISTS idx_payments_decision
    ON payments(decision);

CREATE INDEX IF NOT EXISTS idx_payments_final_outcome
    ON payments(final_outcome);

CREATE INDEX IF NOT EXISTS idx_payments_initiated_at
    ON payments(initiated_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_executed_at
    ON payments(executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_customer_time
    ON payments(customer_id, initiated_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_customer_beneficiary_time
    ON payments(customer_id, beneficiary_id, initiated_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_customer_status_time
    ON payments(customer_id, status, initiated_at DESC);

-- -------------------------
-- payment_events
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_payment_events_payment_id
    ON payment_events(payment_id);

CREATE INDEX IF NOT EXISTS idx_payment_events_event_time
    ON payment_events(event_time DESC);

CREATE INDEX IF NOT EXISTS idx_payment_events_new_status
    ON payment_events(new_status);

CREATE INDEX IF NOT EXISTS idx_payment_events_event_type
    ON payment_events(event_type);

CREATE INDEX IF NOT EXISTS idx_payment_events_payment_time
    ON payment_events(payment_id, event_time DESC);

-- -------------------------
-- risk_assessments
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_risk_assessments_payment_id
    ON risk_assessments(payment_id);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_decision
    ON risk_assessments(decision);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_assessed_at
    ON risk_assessments(assessed_at DESC);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_model_version
    ON risk_assessments(model_version);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_ground_truth_label
    ON risk_assessments(ground_truth_label);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_reason_codes_json
    ON risk_assessments USING GIN (reason_codes_json);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_feature_snapshot_json
    ON risk_assessments USING GIN (feature_snapshot_json);

-- -------------------------
-- analyst_cases
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_analyst_cases_payment_id
    ON analyst_cases(payment_id);

CREATE INDEX IF NOT EXISTS idx_analyst_cases_case_status
    ON analyst_cases(case_status);

CREATE INDEX IF NOT EXISTS idx_analyst_cases_assigned_to
    ON analyst_cases(assigned_to);

CREATE INDEX IF NOT EXISTS idx_analyst_cases_opened_at
    ON analyst_cases(opened_at DESC);

CREATE INDEX IF NOT EXISTS idx_analyst_cases_resolved_at
    ON analyst_cases(resolved_at DESC);

-- -------------------------
-- ledger_entries
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_ledger_entries_account_id
    ON ledger_entries(account_id);

CREATE INDEX IF NOT EXISTS idx_ledger_entries_payment_id
    ON ledger_entries(payment_id);

CREATE INDEX IF NOT EXISTS idx_ledger_entries_entry_type
    ON ledger_entries(entry_type);

CREATE INDEX IF NOT EXISTS idx_ledger_entries_created_at
    ON ledger_entries(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ledger_entries_account_time
    ON ledger_entries(account_id, created_at DESC);