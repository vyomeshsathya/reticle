"""Tests for the database layer (core/db.py)."""

import sqlite3

import pytest

from reticle.core import db

EXPECTED_TABLES = {
    "manufacturers", "models", "generations", "trims",
    "vehicle_aliases", "revlo_tiers", "schema_version",
}


def _table_names(conn):
    """Helper: return the set of table names present in the database."""
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {row["name"] for row in rows}


def test_init_creates_all_tables(tmp_path):
    """A fresh database should contain every expected table."""
    path = db.init_db(tmp_path / "test.db")
    conn = db.connect(path)
    assert EXPECTED_TABLES <= _table_names(conn)
    conn.close()


def test_init_is_idempotent_and_seeds_tiers(tmp_path):
    """Running init_db twice keeps one schema version and seven Revlo tiers."""
    path = tmp_path / "test.db"
    db.init_db(path)
    db.init_db(path)
    conn = db.connect(path)
    assert conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 1
    tiers = conn.execute("SELECT name FROM revlo_tiers ORDER BY sort_order").fetchall()
    assert [t["name"] for t in tiers] == [
        "Common", "Uncommon", "Rare", "Elite", "Exotic", "Legendary", "Mythic",
    ]
    conn.close()


def test_foreign_keys_are_enforced(tmp_path):
    """A model pointing at a missing manufacturer must be rejected."""
    path = db.init_db(tmp_path / "test.db")
    conn = db.connect(path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO models (manufacturer_id, name) VALUES (999, 'Ghost')")
    conn.close()


def test_generation_years_must_be_ordered(tmp_path):
    """A generation that ends before it starts must be rejected."""
    path = db.init_db(tmp_path / "test.db")
    conn = db.connect(path)
    conn.execute("INSERT INTO manufacturers (name) VALUES ('Volkswagen')")
    conn.execute("INSERT INTO models (manufacturer_id, name) VALUES (1, 'Golf')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO generations (model_id, code, year_start, year_end) "
            "VALUES (1, 'Mk8', 2020, 2019)"
        )
    conn.close()


def test_alias_must_point_to_exactly_one_target(tmp_path):
    """An alias with no target (or several) must be rejected."""
    path = db.init_db(tmp_path / "test.db")
    conn = db.connect(path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO vehicle_aliases (alias) VALUES ('golf r')")
    conn.close()