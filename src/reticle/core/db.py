"""Database layer for Reticle: connections and schema migrations.

This module owns everything about opening the SQLite file and keeping its
structure up to date. It never prints or asks for input, so any interface
(the terminal REPL now, a web UI later) can use it.
"""

import os
import sqlite3
from pathlib import Path

# Environment variable that overrides where the database file lives.
DB_ENV_VAR = "RETICLE_DB"

# Default database location, outside the repo so personal data is never committed.
DEFAULT_DB_PATH = Path.home() / ".reticle" / "reticle.db"

# Folder holding schema.sql and future migration files.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Ordered list of (version number, SQL filename). To change the schema later,
# add a new SQL file and append a new entry here; never edit an applied one.
MIGRATIONS = [(1, "schema.sql")]


def get_db_path(db_path=None) -> Path:
    """Return the database file path to use.

    Priority: the explicit argument, then the RETICLE_DB environment
    variable, then the default ~/.reticle/reticle.db.
    """
    if db_path is not None:
        return Path(db_path)
    env_path = os.environ.get(DB_ENV_VAR)
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def connect(db_path=None) -> sqlite3.Connection:
    """Open a connection to the database, creating its folder if needed.

    Rows come back as sqlite3.Row (accessible by column name), foreign keys
    are enforced, and write-ahead logging is on so a second terminal (for
    example the phone over SSH) can read while another writes.
    """
    path = get_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path=None) -> Path:
    """Create the database if needed and bring its schema up to date.

    Overall flow: open a connection, make sure the schema_version table
    exists, find out which migration was applied last, then apply every
    newer migration in order. Running it repeatedly is safe because
    already-applied migrations are skipped.

    Helpers used here: _ensure_version_table, _current_version,
    _apply_migration (which in turn uses _read_migration_sql).

    Returns the path of the database file that was initialised.
    """
    path = get_db_path(db_path)
    conn = connect(path)
    try:
        _ensure_version_table(conn)
        current = _current_version(conn)
        for version, filename in MIGRATIONS:
            if version > current:
                _apply_migration(conn, version, filename)
    finally:
        conn.close()
    return path


def _ensure_version_table(conn: sqlite3.Connection) -> None:
    """Helper for init_db: create the schema_version table if it is missing.

    init_db needs this table to know which migrations already ran, so it
    must exist before any migration is considered.
    """
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version ("
        " version INTEGER PRIMARY KEY,"
        " applied_at TEXT NOT NULL DEFAULT (datetime('now')))"
    )
    conn.commit()


def _current_version(conn: sqlite3.Connection) -> int:
    """Helper for init_db: return the highest applied migration number.

    Returns 0 for a brand-new database. init_db compares this number to
    each entry in MIGRATIONS to decide what still needs to run.
    """
    row = conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()
    return int(row[0])


def _read_migration_sql(filename: str) -> str:
    """Helper for _apply_migration: read one SQL file from the data folder.

    Kept separate so _apply_migration only deals with running SQL, not
    with locating files.
    """
    return (DATA_DIR / filename).read_text(encoding="utf-8")


def _apply_migration(conn: sqlite3.Connection, version: int, filename: str) -> None:
    """Helper for init_db: run one migration file and record its version.

    The SQL and the version bookkeeping run inside a single transaction,
    so a failure rolls everything back and the database is never left
    half-migrated. The error is re-raised so init_db's caller sees it.
    """
    sql = _read_migration_sql(filename)
    script = (
        "BEGIN;\n"
        f"{sql}\n"
        f"INSERT INTO schema_version (version) VALUES ({int(version)});\n"
        "COMMIT;"
    )
    try:
        conn.executescript(script)
    except Exception:
        conn.rollback()
        raise