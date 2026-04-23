

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customer_status') THEN
        CREATE TYPE customer_status AS ENUM ('ACTIVE', 'BLOCKED', 'CLOSED');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_status') THEN
        CREATE TYPE account_status AS ENUM ('ACTIVE', 'FROZEN', 'CLOSED');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'beneficiary_type_enum') THEN
        CREATE TYPE beneficiary_type_enum AS ENUM ('PERSON', 'BUSINESS');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        CREATE TYPE payment_status AS ENUM (
            'PENDING_REVIEW',
            'WARN_ACTION_REQUIRED',
            'USER_CONFIRMED',
            'HELD',
            'RELEASED_BY_ANALYST',
            'APPROVED',
            'SENT_FOR_PAYOUT',
            'PAID_OUT',
            'CANCELLED',
            'DECLINED',
            'PAYOUT_ERROR'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_decision') THEN
        CREATE TYPE risk_decision AS ENUM ('ALLOW', 'WARN', 'HOLD');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_type_enum') THEN
        CREATE TYPE event_type_enum AS ENUM (
            'PAYMENT_CREATED',
            'RISK_ASSESSED',
            'STATUS_CHANGED',
            'WARNING_SHOWN',
            'USER_CONFIRMED_WARNING',
            'USER_CANCELLED',
            'HELD_FOR_REVIEW',
            'CASE_OPENED',
            'CASE_APPROVED',
            'CASE_DECLINED',
            'PAYMENT_APPROVED',
            'PAYMENT_SENT_FOR_PAYOUT',
            'PAYMENT_PAID_OUT',
            'PAYMENT_PAYOUT_ERROR'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'actor_type_enum') THEN
        CREATE TYPE actor_type_enum AS ENUM ('SYSTEM', 'CUSTOMER', 'ANALYST');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'case_status_enum') THEN
        CREATE TYPE case_status_enum AS ENUM ('OPEN', 'IN_REVIEW', 'APPROVED', 'DECLINED');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ledger_entry_type_enum') THEN
        CREATE TYPE ledger_entry_type_enum AS ENUM ('DEBIT', 'CREDIT', 'REVERSAL');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'final_outcome_type') THEN
        CREATE TYPE final_outcome_type AS ENUM ('SUCCESS', 'CANCELLED', 'DECLINED', 'ERROR');
    END IF;
END $$;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

