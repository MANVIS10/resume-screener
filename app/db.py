import os
from contextlib import contextmanager

import libsql

SCHEMA = """
CREATE TABLE IF NOT EXISTS jds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    jd_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jd_id INTEGER NOT NULL REFERENCES jds(id),
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    age TEXT NOT NULL,
    location TEXT NOT NULL,
    resume_text TEXT NOT NULL,
    match_score INTEGER,
    fit_summary TEXT,
    gaps_json TEXT,
    submitted_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@contextmanager
def db_session():
    """Open a short-lived connection.

    TURSO_DATABASE_URL is either a remote Turso URL (``libsql://...``), which
    libsql opens over HTTP without touching the filesystem, or a plain file
    path for local development. Serverless functions get a read-only disk, so
    the remote form is the only one that works once deployed.
    """
    url = os.environ.get("TURSO_DATABASE_URL")
    if not url:
        raise RuntimeError("TURSO_DATABASE_URL is not set")

    conn = libsql.connect(url, auth_token=os.environ.get("TURSO_AUTH_TOKEN", ""))
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _rows_to_dicts(cursor) -> list[dict]:
    columns = [c[0] for c in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def query(sql: str, params: tuple = ()) -> list[dict]:
    with db_session() as conn:
        return _rows_to_dicts(conn.execute(sql, params))


def query_one(sql: str, params: tuple = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple = ()) -> None:
    with db_session() as conn:
        conn.execute(sql, params)


def init_db() -> None:
    """Create tables. Run once as a migration, not per request."""
    with db_session() as conn:
        conn.executescript(SCHEMA)
