--create schema
CREATE SCHEMA IF NOT EXISTS supplieraudit;

--create tables
CREATE TABLE supplieraudit.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    role VARCHAR(100),
    password VARCHAR(255),
    supplier_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE supplieraudit.supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zip VARCHAR(20),
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

CREATE TABLE supplieraudit.audit_template (
    template_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_edited_ts TIMESTAMP,
    last_edited_by INTEGER,
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

CREATE TABLE supplieraudit.audit_template_group (
    group_id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    name VARCHAR(255),
    weight FLOAT,
    last_edited_ts TIMESTAMP,
    last_edited_by INTEGER,
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    CONSTRAINT fk_template
        FOREIGN KEY (template_id)
        REFERENCES supplieraudit.audit_template(template_id)
        ON DELETE CASCADE
);

CREATE TABLE supplieraudit.audit_template_question (
    question_id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    question_text VARCHAR(500),
    mandatory VARCHAR(10),
    last_edited_ts TIMESTAMP,
    last_edited_by INTEGER,
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    CONSTRAINT fk_group
        FOREIGN KEY (group_id)
        REFERENCES supplieraudit.audit_template_group(group_id)
        ON DELETE CASCADE
);

CREATE TABLE supplieraudit.audit (
    audit_id SERIAL PRIMARY KEY,
    auditor_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    total_score FLOAT,
    draft VARCHAR(10),
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_edited_ts TIMESTAMP,
    CONSTRAINT fk_auditor
        FOREIGN KEY (auditor_id)
        REFERENCES supplieraudit.users(id),
    CONSTRAINT fk_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES supplieraudit.supplier(supplier_id)
);

CREATE TABLE supplieraudit.audit_finding (
    finding_id SERIAL PRIMARY KEY,
    audit_id INTEGER NOT NULL,
    score FLOAT,
    question_id INTEGER,
    last_edited_ts TIMESTAMP,
    CONSTRAINT fk_audit_finding
        FOREIGN KEY (audit_id)
        REFERENCES supplieraudit.audit(audit_id)
        ON DELETE CASCADE
);

CREATE TABLE supplieraudit.action_item (
    action_item_id SERIAL PRIMARY KEY,
    audit_id INTEGER NOT NULL,
    item_text VARCHAR(500),
    root_cause VARCHAR(500),
    corrective_action VARCHAR(500),
    preventive_action VARCHAR(500),
    status VARCHAR(50),
    responder_id INTEGER,
    CONSTRAINT fk_action_audit
        FOREIGN KEY (audit_id)
        REFERENCES supplieraudit.audit(audit_id)
        ON DELETE CASCADE
);

-- foreign keys
ALTER TABLE supplieraudit.users
ADD CONSTRAINT fk_user_supplier
FOREIGN KEY (supplier_id)
REFERENCES supplieraudit.supplier(supplier_id);

ALTER TABLE supplieraudit.supplier
ADD CONSTRAINT fk_supplier_created_by
FOREIGN KEY (created_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.audit_template
ADD CONSTRAINT fk_template_created_by
FOREIGN KEY (created_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.audit_template
ADD CONSTRAINT fk_template_last_edited_by
FOREIGN KEY (last_edited_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.audit_template_group
ADD CONSTRAINT fk_group_created_by
FOREIGN KEY (created_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.audit_template_group
ADD CONSTRAINT fk_group_last_edited_by
FOREIGN KEY (last_edited_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.audit_template_question
ADD CONSTRAINT fk_question_created_by
FOREIGN KEY (created_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.audit_template_question
ADD CONSTRAINT fk_question_last_edited_by
FOREIGN KEY (last_edited_by)
REFERENCES supplieraudit.users(id);

ALTER TABLE supplieraudit.action_item
ADD CONSTRAINT fk_action_responder
FOREIGN KEY (responder_id)
REFERENCES supplieraudit.users(id);