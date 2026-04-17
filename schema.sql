-- Archives World Map - SQLite Schema (simplified)

CREATE TABLE IF NOT EXISTS institutions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT    NOT NULL,
    latitude           REAL    NOT NULL,
    longitude          REAL    NOT NULL,
    address            TEXT,
    city               TEXT,
    district           TEXT,
    country            TEXT,
    url                TEXT,
    email              TEXT,
    identifier         TEXT,
    status             TEXT    NOT NULL DEFAULT 'waiting',  -- waiting | verified | rejected
    token              TEXT    UNIQUE NOT NULL,
    collaborator_name  TEXT    NOT NULL,
    collaborator_email TEXT    NOT NULL,
    admin_notes        TEXT,
    submitted_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
    moderated_at       TEXT
);

CREATE INDEX IF NOT EXISTS idx_status  ON institutions(status);
CREATE INDEX IF NOT EXISTS idx_token   ON institutions(token);
CREATE INDEX IF NOT EXISTS idx_country ON institutions(country);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS password_resets (
    id         INTEGER PRIMARY KEY,
    hash       TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    username           TEXT NOT NULL UNIQUE,
    email              TEXT NOT NULL UNIQUE,
    password_hash      TEXT NOT NULL,
    can_approve        INTEGER NOT NULL DEFAULT 0,
    can_edit_waiting   INTEGER NOT NULL DEFAULT 0,
    can_edit_verified  INTEGER NOT NULL DEFAULT 0,
    is_active          INTEGER NOT NULL DEFAULT 1,
    must_change_password INTEGER NOT NULL DEFAULT 0,
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
