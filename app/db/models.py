CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id              BIGSERIAL PRIMARY KEY,
    telegram_id     BIGINT UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS servers (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ip              VARCHAR(45) NOT NULL,
    port            INTEGER NOT NULL,
    protocol        VARCHAR(50) NOT NULL DEFAULT 'other',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_status     BOOLEAN,                    -- True = online, False = offline, NULL = ещё не проверяли
    last_check      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (user_id, ip, port)
);

CREATE INDEX IF NOT EXISTS idx_servers_user_id ON servers(user_id);
CREATE INDEX IF NOT EXISTS idx_servers_active ON servers(is_active);
"""
