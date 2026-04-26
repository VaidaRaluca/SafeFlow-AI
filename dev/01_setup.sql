-- 01_setup.sql
-- SafeFlow AI - PostgreSQL setup
-- Rulează acest script primul.

BEGIN;

-- Extensie pentru UUID-uri generate în PostgreSQL.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Namespace dedicat aplicației.
CREATE SCHEMA IF NOT EXISTS safeflow;

-- Enum-uri folosite de tabelele aplicației.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'currency_code' AND typnamespace = 'safeflow'::regnamespace) THEN
        CREATE TYPE safeflow.currency_code AS ENUM ('EUR', 'RON', 'USD', 'GBP');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transaction_status' AND typnamespace = 'safeflow'::regnamespace) THEN
        CREATE TYPE safeflow.transaction_status AS ENUM (
            'PENDING',
            'APPROVED',
            'WARNED',
            'SETTLED',
            'CANCELED',
            'REJECTED'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_level' AND typnamespace = 'safeflow'::regnamespace) THEN
        CREATE TYPE safeflow.risk_level AS ENUM ('LOW', 'MEDIUM', 'HIGH');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_decision' AND typnamespace = 'safeflow'::regnamespace) THEN
        CREATE TYPE safeflow.risk_decision AS ENUM ('ALLOW', 'WARN', 'REJECT');
    END IF;
END $$;

COMMIT;
