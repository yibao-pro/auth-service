-- Auth service PostgreSQL schema
-- Minimal isolated schema extracted from the legacy Yibao project.

BEGIN;

CREATE TABLE IF NOT EXISTS public.users (
    id bigserial PRIMARY KEY,
    user_id varchar(36) NOT NULL UNIQUE,
    username varchar(64) NOT NULL UNIQUE,
    password_hash varchar(255) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
