-- 01_setup.sql
-- SafeFlow AI - PostgreSQL setup (fără schemă)

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Șterge enum-urile dacă există (important pentru rerun)
DROP TYPE IF EXISTS currency_code CASCADE;
DROP TYPE IF EXISTS transaction_status CASCADE;
DROP TYPE IF EXISTS risk_level CASCADE;
DROP TYPE IF EXISTS risk_decision CASCADE;

-- Enum-uri globale (public schema)
CREATE TYPE currency_code AS ENUM ('EUR', 'RON', 'USD', 'GBP');

CREATE TYPE transaction_status AS ENUM (
    'PENDING',
    'APPROVED',
    'WARNED',
    'SETTLED',
    'CANCELED',
    'REJECTED'
);

CREATE TYPE risk_level AS ENUM ('LOW', 'MEDIUM', 'HIGH');

CREATE TYPE risk_decision AS ENUM ('ALLOW', 'WARN', 'REJECT');

COMMIT;