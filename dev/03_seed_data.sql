-- 03_seed_data.sql
-- SafeFlow AI - PostgreSQL seed data, SQL-only version
-- Rulează după:
--   01_setup.sql
--   02_tables.sql
--
-- Rulează:
--   psql -d safeflow_db -U postgres -f 03_seed_data.sql
--
-- Ce creează:
--   - 85 users cu nume/emailuri realiste
--   - 85 accounts cu IBAN-uri unice
--   - 500 transactions
--   - 500 risk_assessments
--   - contacts cu is_trusted = TRUE după minimum 5 tranzacții APPROVED
--
-- Include scenarii:
--   1. beneficiar trusted: minimum 5 plăți APPROVED
--   2. beneficiar nou + sumă mare: WARNED
--   3. mesaj urgent + oră neobișnuită: REJECTED
--   4. gradual trust building: 3 plăți mici, apoi una mare
--   5. tranzacții normale, warning și rejected mixte

BEGIN;

TRUNCATE TABLE risk_assessments, transactions, contacts, accounts, users RESTART IDENTITY CASCADE;

-- =========================================================
-- 1. Users realiști, dar generați static
-- =========================================================

DROP TABLE IF EXISTS tmp_seed_people;
DROP TABLE IF EXISTS tmp_accounts;
DROP TABLE IF EXISTS tmp_scenario_accounts;

CREATE TEMP TABLE tmp_seed_people (
    n int PRIMARY KEY,
    full_name varchar(150) NOT NULL,
    email varchar(255) NOT NULL UNIQUE,
    balance numeric(14,2) NOT NULL
);

INSERT INTO tmp_seed_people (n, full_name, email, balance) VALUES
(1, 'Andrei Popescu', 'andrei.popescu@example.test', 9500.00),
(2, 'Maria Ionescu', 'maria.ionescu@example.test', 3200.00),
(3, 'Vlad Georgescu', 'vlad.georgescu@example.test', 1200.00),
(4, 'Ioana Dumitrescu', 'ioana.dumitrescu@example.test', 300.00),
(5, 'Elena Stan', 'elena.stan@example.test', 15000.00),
(6, 'Mihai Radu', 'mihai.radu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(7, 'Ana Marinescu', 'ana.marinescu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(8, 'Cristian Stoica', 'cristian.stoica@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(9, 'Bianca Pavel', 'bianca.pavel@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(10, 'Radu Enache', 'radu.enache@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(11, 'Diana Ilie', 'diana.ilie@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(12, 'Sorin Matei', 'sorin.matei@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(13, 'Alexandra Tudor', 'alexandra.tudor@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(14, 'George Florea', 'george.florea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(15, 'Irina Dobre', 'irina.dobre@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(16, 'Paul Neagu', 'paul.neagu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(17, 'Laura Barbu', 'laura.barbu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(18, 'Daniel Oprea', 'daniel.oprea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(19, 'Monica Serban', 'monica.serban@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(20, 'Adrian Nita', 'adrian.nita@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(21, 'Raluca Petrescu', 'raluca.petrescu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(22, 'Victor Anghel', 'victor.anghel@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(23, 'Oana Cristea', 'oana.cristea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(24, 'Stefan Moldovan', 'stefan.moldovan@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(25, 'Gabriela Toma', 'gabriela.toma@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(26, 'Lucian Voicu', 'lucian.voicu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(27, 'Simona Preda', 'simona.preda@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(28, 'Catalin Munteanu', 'catalin.munteanu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(29, 'Alina Badea', 'alina.badea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(30, 'Florin Sandu', 'florin.sandu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(31, 'Nicoleta Rusu', 'nicoleta.rusu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(32, 'Bogdan Sava', 'bogdan.sava@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(33, 'Carmen Lazar', 'carmen.lazar@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(34, 'Ionut Dragomir', 'ionut.dragomir@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(35, 'Roxana Filip', 'roxana.filip@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(36, 'Claudiu Zaharia', 'claudiu.zaharia@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(37, 'Lavinia Ene', 'lavinia.ene@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(38, 'Tudor Popa', 'tudor.popa@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(39, 'Anca Nechita', 'anca.nechita@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(40, 'Mircea Pavelescu', 'mircea.pavelescu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(41, 'Denisa Lupu', 'denisa.lupu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(42, 'Razvan Ciobanu', 'razvan.ciobanu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(43, 'Camelia Grigore', 'camelia.grigore@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(44, 'Marius Dinu', 'marius.dinu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(45, 'Teodora Avram', 'teodora.avram@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(46, 'Silviu Bucur', 'silviu.bucur@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(47, 'Adina Mocanu', 'adina.mocanu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(48, 'Cosmin Aldea', 'cosmin.aldea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(49, 'Madalina Dinca', 'madalina.dinca@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(50, 'Octavian Iliescu', 'octavian.iliescu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(51, 'Iulia Zamfir', 'iulia.zamfir@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(52, 'Sebastian Marin', 'sebastian.marin@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(53, 'Larisa Gheorghe', 'larisa.gheorghe@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(54, 'Emanuel Radu', 'emanuel.radu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(55, 'Paula Stanciu', 'paula.stanciu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(56, 'Vasile Cojocaru', 'vasile.cojocaru@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(57, 'Corina Manea', 'corina.manea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(58, 'Robert Cretu', 'robert.cretu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(59, 'Mihaela Ene', 'mihaela.ene@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(60, 'Alexandru Ilinca', 'alexandru.ilinca@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(61, 'Ema Vasile', 'ema.vasile@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(62, 'Dorin Pavel', 'dorin.pavel@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(63, 'Sonia Baciu', 'sonia.baciu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(64, 'Marian Nistor', 'marian.nistor@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(65, 'Felicia Sima', 'felicia.sima@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(66, 'Horia Roman', 'horia.roman@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(67, 'Beatrice Vlad', 'beatrice.vlad@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(68, 'Sergiu Tatu', 'sergiu.tatu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(69, 'Natalia Chivu', 'natalia.chivu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(70, 'Ciprian Dima', 'ciprian.dima@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(71, 'Loredana Iacob', 'loredana.iacob@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(72, 'Valentin Tiron', 'valentin.tiron@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(73, 'Georgiana Luca', 'georgiana.luca@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(74, 'Darius Balan', 'darius.balan@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(75, 'Ariana Pascu', 'ariana.pascu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(76, 'Liviu Istrate', 'liviu.istrate@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(77, 'Carla Mateescu', 'carla.mateescu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(78, 'Tiberiu Fratila', 'tiberiu.fratila@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(79, 'Mara Costache', 'mara.costache@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(80, 'Eduard Mocanu', 'eduard.mocanu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(81, 'Daria Voinea', 'daria.voinea@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(82, 'Rares Lupescu', 'rares.lupescu@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(83, 'Ilinca Moraru', 'ilinca.moraru@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(84, 'Narcis Botez', 'narcis.botez@example.test', ROUND((250 + random() * 19750)::numeric, 2)),
(85, 'Amalia Olaru', 'amalia.olaru@example.test', ROUND((250 + random() * 19750)::numeric, 2));

WITH inserted_users AS (
    INSERT INTO users (full_name, email, password_hash)
    SELECT
        full_name,
        email,
        '$2b$12$demoHashedPasswordForSafeFlowOnly'
    FROM tmp_seed_people
    RETURNING id, email
)
INSERT INTO accounts (user_id, iban, balance, currency)
SELECT
    u.id,
    'RO49AAAA1B310075' || LPAD(p.n::text, 8, '0'),
    p.balance,
    'EUR'
FROM inserted_users u
JOIN tmp_seed_people p ON p.email = u.email;

-- =========================================================
-- 2. Temp account map
-- =========================================================

CREATE TEMP TABLE tmp_accounts AS
SELECT
    a.id AS account_id,
    u.email,
    row_number() OVER (ORDER BY u.email) AS rn
FROM accounts a
JOIN users u ON u.id = a.user_id;

-- Aceste roluri sunt doar pentru seed logic, nu apar în users.
CREATE TEMP TABLE tmp_scenario_accounts AS
SELECT
    MAX(account_id::text) FILTER (WHERE email = 'andrei.popescu@example.test')::uuid AS primary_sender,
    MAX(account_id::text) FILTER (WHERE email = 'maria.ionescu@example.test')::uuid AS trusted_receiver,
    MAX(account_id::text) FILTER (WHERE email = 'vlad.georgescu@example.test')::uuid AS new_receiver,
    MAX(account_id::text) FILTER (WHERE email = 'ioana.dumitrescu@example.test')::uuid AS suspicious_receiver,
    MAX(account_id::text) FILTER (WHERE email = 'elena.stan@example.test')::uuid AS business_receiver
FROM tmp_accounts;

-- =========================================================
-- 3. Scenarii explicite
-- =========================================================

-- A. Trusted beneficiary: 5 plăți approved.
INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    s.primary_sender,
    s.trusted_receiver,
    (25 + gs * 10)::numeric(14,2),
    'EUR',
    'plata recurenta ' || gs,
    'APPROVED',
    now() - ((30 - gs) || ' days')::interval,
    now() - ((30 - gs) || ' days')::interval,
    now() - ((30 - gs) || ' days')::interval,
    false
FROM tmp_scenario_accounts s
CROSS JOIN generate_series(1, 5) gs;

-- B. Beneficiar nou + sumă mare => WARNED.
INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    primary_sender,
    new_receiver,
    3500.00,
    'EUR',
    'transfer beneficiar nou suma ridicata',
    'WARNED',
    now() - interval '2 days 3 hours',
    now() - interval '2 days 3 hours' + interval '10 minutes',
    now() - interval '2 days 3 hours' + interval '10 minutes',
    true
FROM tmp_scenario_accounts;

-- C. Mesaj urgent + timing neobișnuit => REJECTED.
INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    primary_sender,
    suspicious_receiver,
    1800.00,
    'EUR',
    'urgent verificare cont imediat',
    'REJECTED',
    date_trunc('day', now() - interval '1 day') + interval '23 hours 45 minutes',
    date_trunc('day', now() - interval '1 day') + interval '23 hours 50 minutes',
    date_trunc('day', now() - interval '1 day') + interval '23 hours 50 minutes',
    false
FROM tmp_scenario_accounts;

-- D. Gradual trust building: 3 plăți mici, apoi o sumă mare.
INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    s.primary_sender,
    s.suspicious_receiver,
    100.00,
    'EUR',
    'transfer personal ' || gs,
    'APPROVED',
    now() - ((10 - gs) || ' days')::interval,
    now() - ((10 - gs) || ' days')::interval,
    now() - ((10 - gs) || ' days')::interval,
    false
FROM tmp_scenario_accounts s
CROSS JOIN generate_series(1, 3) gs;

INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    primary_sender,
    suspicious_receiver,
    1000.00,
    'EUR',
    'transfer personal suma mare',
    'REJECTED',
    now() - interval '5 hours',
    now() - interval '5 hours' + interval '5 minutes',
    now() - interval '5 hours' + interval '5 minutes',
    false
FROM tmp_scenario_accounts;

-- E. Business receiver legitim: plăți approved.
INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    s.primary_sender,
    s.business_receiver,
    ROUND((400 + random() * 550)::numeric, 2),
    'EUR',
    'factura servicii ' || gs,
    'APPROVED',
    now() - ((20 - gs) || ' days')::interval,
    now() - ((20 - gs) || ' days')::interval,
    now() - ((20 - gs) || ' days')::interval,
    false
FROM tmp_scenario_accounts s
CROSS JOIN generate_series(1, 4) gs;

-- =========================================================
-- 4. Tranzacții random realiste
--    15 explicite + 485 random = 500 total
-- =========================================================

WITH tx_source AS (
    SELECT
        gs,
        s.account_id AS sender_id,
        r.account_id AS receiver_id,
        random() AS scenario_roll,
        now()
            - ((1 + floor(random() * 120))::int || ' days')::interval
            - ((floor(random() * 24))::int || ' hours')::interval
            - ((floor(random() * 60))::int || ' minutes')::interval AS created_at
    FROM generate_series(1, 485) gs
    CROSS JOIN LATERAL (
        SELECT account_id
        FROM tmp_accounts
        ORDER BY random()
        LIMIT 1
    ) s
    CROSS JOIN LATERAL (
        SELECT account_id
        FROM tmp_accounts
        WHERE account_id <> s.account_id
        ORDER BY random()
        LIMIT 1
    ) r
),
classified AS (
    SELECT
        gs,
        sender_id,
        receiver_id,
        created_at,
        CASE
            WHEN scenario_roll < 0.60 THEN 'normal'
            WHEN scenario_roll < 0.72 THEN 'new_high_value'
            WHEN scenario_roll < 0.84 THEN 'urgent_night'
            WHEN scenario_roll < 0.94 THEN 'medium_warning'
            ELSE 'hard_reject'
        END AS scenario
    FROM tx_source
),
prepared AS (
    SELECT
        sender_id,
        receiver_id,
        CASE
            WHEN scenario = 'normal' THEN ROUND((5 + random() * 245)::numeric, 2)
            WHEN scenario = 'new_high_value' THEN ROUND((1200 + random() * 3300)::numeric, 2)
            WHEN scenario = 'urgent_night' THEN ROUND((300 + random() * 2200)::numeric, 2)
            WHEN scenario = 'medium_warning' THEN ROUND((250 + random() * 650)::numeric, 2)
            ELSE ROUND((1500 + random() * 5500)::numeric, 2)
        END AS amount,
        CASE
            WHEN scenario = 'normal' THEN
                (ARRAY[
                    'cina',
                    'chirie',
                    'cadou',
                    'factura utilitati',
                    'abonament',
                    'cumparaturi',
                    'transport',
                    'servicii'
                ])[1 + floor(random() * 8)::int]
            WHEN scenario = 'new_high_value' THEN
                (ARRAY[
                    'transfer beneficiar nou',
                    'avans achizitie',
                    'plata rezervare',
                    'transfer suma ridicata'
                ])[1 + floor(random() * 4)::int]
            WHEN scenario = 'urgent_night' THEN
                (ARRAY[
                    'urgent plata necesara',
                    'verificare cont imediat',
                    'transfer rapid te rog',
                    'problema cont',
                    'ajutor familie urgent',
                    'taxa spital imediat'
                ])[1 + floor(random() * 6)::int]
            WHEN scenario = 'medium_warning' THEN
                (ARRAY[
                    'verificare plata beneficiar nou',
                    'transfer confirmare',
                    'plata catre contact recent',
                    'transfer neobisnuit'
                ])[1 + floor(random() * 4)::int]
            ELSE
                (ARRAY[
                    'urgent investitie',
                    'taxa premiu',
                    'blocare cont transfer imediat',
                    'plata risc ridicat',
                    'confirmare castig'
                ])[1 + floor(random() * 5)::int]
        END AS description,
        CASE
            WHEN scenario = 'normal' THEN 'APPROVED'::transaction_status
            WHEN scenario = 'medium_warning' THEN 'WARNED'::transaction_status
            WHEN scenario = 'new_high_value' AND random() < 0.55 THEN 'WARNED'::transaction_status
            WHEN scenario = 'new_high_value' THEN 'REJECTED'::transaction_status
            WHEN scenario = 'urgent_night' AND random() < 0.45 THEN 'WARNED'::transaction_status
            WHEN scenario = 'urgent_night' THEN 'REJECTED'::transaction_status
            ELSE 'REJECTED'::transaction_status
        END AS status,
        CASE
            WHEN scenario = 'urgent_night'
                THEN date_trunc('day', created_at)
                    + ((ARRAY[22,23,0,1,2,3,4])[1 + floor(random() * 7)::int] || ' hours')::interval
            ELSE created_at
        END AS created_at
    FROM classified
)
INSERT INTO transactions (
    sender_id, receiver_id, amount, currency, description, status,
    created_at, confirmed_at, settled_at, requires_password_confirmation
)
SELECT
    sender_id,
    receiver_id,
    amount,
    'EUR',
    description,
    status,
    created_at,
    CASE
        WHEN status = 'APPROVED' THEN created_at
        WHEN status = 'WARNED' THEN created_at + interval '10 minutes'
        WHEN status = 'REJECTED' THEN created_at + interval '5 minutes'
        ELSE NULL
    END AS confirmed_at,
    CASE
        WHEN status = 'APPROVED' THEN created_at
        WHEN status = 'WARNED' THEN created_at + interval '10 minutes'
        WHEN status = 'REJECTED' THEN created_at + interval '5 minutes'
        ELSE NULL
    END AS settled_at,
    status = 'WARNED'
FROM prepared;

-- =========================================================
-- 5. Risk assessments
-- =========================================================

INSERT INTO risk_assessments (
    transaction_id,
    rule_score,
    anomaly_score,
    combined_score,
    risk_level,
    decision,
    evaluated_at
)
SELECT
    scored.transaction_id,
    scored.rule_score,
    scored.anomaly_score,
    scored.combined_score,
    scored.risk_level,
    scored.decision,
    scored.created_at + interval '5 seconds'
FROM (
    SELECT
        t.id AS transaction_id,
        t.created_at,
        CASE
            WHEN t.status = 'APPROVED' THEN ROUND((0.02 + random() * 0.33)::numeric, 3)
            WHEN t.status = 'WARNED' THEN ROUND((0.35 + random() * 0.35)::numeric, 3)
            WHEN t.status = 'REJECTED' THEN ROUND((0.70 + random() * 0.30)::numeric, 3)
            ELSE 0.000::numeric
        END AS rule_score,
        CASE
            WHEN t.status = 'APPROVED' THEN ROUND((0.02 + random() * 0.33)::numeric, 3)
            WHEN t.status = 'WARNED' THEN ROUND((0.30 + random() * 0.40)::numeric, 3)
            WHEN t.status = 'REJECTED' THEN ROUND((0.65 + random() * 0.35)::numeric, 3)
            ELSE 0.000::numeric
        END AS anomaly_score,
        CASE
            WHEN t.status = 'APPROVED' THEN 'LOW'::risk_level
            WHEN t.status = 'WARNED' THEN 'MEDIUM'::risk_level
            WHEN t.status = 'REJECTED' THEN 'HIGH'::risk_level
            ELSE 'LOW'::risk_level
        END AS risk_level,
        CASE
            WHEN t.status = 'APPROVED' THEN 'ALLOW'::risk_decision
            WHEN t.status = 'WARNED' THEN 'WARN'::risk_decision
            WHEN t.status = 'REJECTED' THEN 'REJECT'::risk_decision
            ELSE 'ALLOW'::risk_decision
        END AS decision
    FROM transactions t
) base
CROSS JOIN LATERAL (
    SELECT
        base.transaction_id,
        base.created_at,
        base.rule_score,
        base.anomaly_score,
        CASE
            WHEN base.risk_level = 'LOW' THEN LEAST(base.rule_score + base.anomaly_score, 0.740)
            WHEN base.risk_level = 'MEDIUM' THEN GREATEST(0.750, LEAST(base.rule_score + base.anomaly_score, 1.240))
            ELSE GREATEST(base.rule_score + base.anomaly_score, 1.250)
        END::numeric(4,3) AS combined_score,
        base.risk_level,
        base.decision
) scored;

-- =========================================================
-- 6. Contacts
-- =========================================================

INSERT INTO contacts (sender_id, receiver_id, is_trusted)
SELECT
    t.sender_id,
    t.receiver_id,
    CASE
        WHEN COUNT(*) FILTER (WHERE t.status = 'APPROVED') >= 5 THEN TRUE
        ELSE FALSE
    END AS is_trusted
FROM transactions t
GROUP BY t.sender_id, t.receiver_id
ON CONFLICT (sender_id, receiver_id)
DO UPDATE SET is_trusted = EXCLUDED.is_trusted;

-- =========================================================
-- 7. Summary
-- =========================================================

DO $$
DECLARE
    users_count int;
    accounts_count int;
    contacts_count int;
    tx_count int;
    risk_count int;
BEGIN
    SELECT COUNT(*) INTO users_count FROM users;
    SELECT COUNT(*) INTO accounts_count FROM accounts;
    SELECT COUNT(*) INTO contacts_count FROM contacts;
    SELECT COUNT(*) INTO tx_count FROM transactions;
    SELECT COUNT(*) INTO risk_count FROM risk_assessments;

    RAISE NOTICE 'Seed completed successfully.';
    RAISE NOTICE 'Users: %', users_count;
    RAISE NOTICE 'Accounts: %', accounts_count;
    RAISE NOTICE 'Contacts: %', contacts_count;
    RAISE NOTICE 'Transactions: %', tx_count;
    RAISE NOTICE 'Risk assessments: %', risk_count;
    RAISE NOTICE 'Main test sender email: andrei.popescu@example.test';
    RAISE NOTICE 'Trusted receiver email: maria.ionescu@example.test';
    RAISE NOTICE 'High-value new receiver email: vlad.georgescu@example.test';
    RAISE NOTICE 'Urgent/night receiver email: ioana.dumitrescu@example.test';
END $$;

COMMIT;
