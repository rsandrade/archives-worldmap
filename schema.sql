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
