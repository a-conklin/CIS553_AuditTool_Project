-- Use schema
SET search_path TO supplieraudit;

-- =========================
-- Insert Supplier
-- =========================
INSERT INTO supplier (
    name,
    address,
    city,
    state,
    country,
    zip,
    created_ts,
    created_by
)
VALUES (
    'Test Supplier Inc.',
    '123 Test St',
    'Testville',
    'MI',
    'USA',
    '12345',
    NOW(),
    1
);


-- =========================
-- Insert Admin User
-- =========================
INSERT INTO users (
    username,
    email,
    role,
    password,
    supplier_id,
    created_at
)
VALUES (
    'admin',
    'admin@test.com',
    'admin',
    '123',
    NULL,
    NOW()
);


-- =========================
-- Insert Supplier User
-- =========================
INSERT INTO users (
    username,
    email,
    role,
    password,
    supplier_id,
    created_at
)
VALUES (
    'supplier_user',
    'supplier@test.com',
    '',
    '123',
    1,           -- might not work as expected if not used as a fresh install
    NOW()
);