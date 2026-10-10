"""Interactive terminal interface for Reticle (placeholder until the real REPL)."""

from reticle.core.db import init_db


def main() -> None:
    """Start Reticle: make sure the database exists and is current, then greet.

    This is a stand-in for the full REPL. It calls init_db (from core/db.py),
    which creates or upgrades the database, then reports where it lives.
    """
    db_path = init_db()
    print("RETICLE ONLINE")
    print(f"Database ready: {db_path}")