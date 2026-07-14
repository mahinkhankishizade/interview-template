CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    full_name   TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);




CREATE TABLE IF NOT EXISTS conversations (
    id          SERIAL PRIMARY KEY,
    quality_metric BOOLEAN,  -- nullable; NULL until the conversation is scored
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS query (
    id         SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    is_input   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE
);

ALTER TABLE conversations ADD COLUMN IF NOT EXISTS llm_model TEXT NOT NULL DEFAULT 'A';