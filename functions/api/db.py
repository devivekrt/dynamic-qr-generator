import sqlite3
import secrets

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS businesses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    slug          TEXT NOT NULL UNIQUE,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id   INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    qr_code_id    INTEGER REFERENCES qr_codes(id) ON DELETE CASCADE,
    title         TEXT NOT NULL,
    type          TEXT NOT NULL CHECK (type IN ('text', 'link', 'image', 'pdf')),
    text_value    TEXT,
    url_value     TEXT,
    file_name     TEXT,
    original_name TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contents_business ON contents(business_id);

CREATE TABLE IF NOT EXISTS qr_codes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id   INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name          TEXT NOT NULL,
    slug          TEXT NOT NULL UNIQUE,
    created_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_qr_codes_business ON qr_codes(business_id);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = connect()
    conn.executescript(SCHEMA)
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(contents)")}
    if "qr_code_id" not in columns:
        conn.execute("ALTER TABLE contents ADD COLUMN qr_code_id INTEGER REFERENCES qr_codes(id)")

    businesses = conn.execute("SELECT id, name, slug, created_at FROM businesses").fetchall()
    for business in businesses:
        qr = conn.execute(
            "SELECT id FROM qr_codes WHERE business_id = ? ORDER BY id LIMIT 1",
            (business["id"],),
        ).fetchone()
        if qr is None:
            slug = business["slug"]
            while conn.execute("SELECT 1 FROM qr_codes WHERE slug = ?", (slug,)).fetchone():
                slug = f"{business['slug']}-{secrets.token_hex(2)}"
            cur = conn.execute(
                "INSERT INTO qr_codes (business_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
                (business["id"], "Main QR code", slug, business["created_at"]),
            )
            qr_id = cur.lastrowid
        else:
            qr_id = qr["id"]
        conn.execute(
            "UPDATE contents SET qr_code_id = ? WHERE business_id = ? AND qr_code_id IS NULL",
            (qr_id, business["id"]),
        )
    conn.commit()
    conn.close()


def get_db():
    """FastAPI dependency: one connection per request."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
