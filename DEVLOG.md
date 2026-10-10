# RETICLE DEV LOG

## October 9 / 2026 -- Session 1
**Start**
- Goal: Set up the Reticle project scaffold, get a working 'reticle' command and publish to GitHub.
- Starting state: empty scaffold, no code

**End**
- Done:
    - Chose the project name (Reticle) and the src-layout structure: `core/` for logic, `cli/` for the interface, `data/` for schema and seed data.
    - Created the Git repo and a Python 3.13 virtual environment.
    - Wrote `pyproject.toml` with dependencies (`rich`, `prompt_toolkit`) and the `reticle` console entry point.
    - Installed the package in editable mode; both `reticle` and `python -m reticle` print `RETICLE ONLINE`.
    - Added `.gitignore` and MIT `LICENSE`, and published the repo as public on GitHub.
- Problems hit and fixes:
    - PowerShell blocked venv activation (execution policy). Fixed with `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
    - First `pip install -e .` produced version 0.0.0 with no `reticle` command because `pyproject.toml` was unsaved/empty. Saved the files and reinstalled.
- Broken / unfinished:
    - `README.md` is a placeholder, and `docs/` and `tests/` are empty.
    - No database and vehicle records yet.
- Next session starts with: designing `schema.sql` (manufacturer -> model -> generation -> trim), then the DB connection and migrations in `core/db.py`
- Commit(s): "Initial project scaffold"

## October 10 / 2026 -- Session 02
**Start**
- Goal: Design the SQLite schma (manufacturer -> model -> generation -> trim, plus aliases and schema_version) and write core/db.py to open the database and apply the schema.
- Starting state: scaffold pushed to Github; `reticle` prints RETICLE ONLINE; schema.sql and db.py are empty
- Open decisions: how to model Revlo tiers; how to model drives from Wheelz (manual entry only).

**End**
- Done:
  - Designed the catalog schema: manufacturers → models → generations → trims, plus vehicle_aliases and a seeded revlo_tiers table (7 tiers with XP).
  - Revlo tier is stored per trim; project rarity score is a separate nullable 0-10 column; unknown specs are NULL.
  - Wrote core/db.py: connection setup (foreign keys, WAL), versioned migrations, and a database stored at ~/.reticle/reticle.db (override with RETICLE_DB).
  - `reticle` now creates/updates the database on launch.
  - Added 5 pytest tests covering table creation, idempotent init, foreign keys, year ordering and alias targets.
- Problems hit and fixes:
  - (add anything that went wrong)
- Broken / unfinished:
  - No vehicle data yet; spots, drives and garage tables not designed.
- Decisions: Revlo generation labels (e.g. Mk7.5, W463A) are stored as their own generation rows; city/colour/time belong to spots (V0.2), not the catalog.
- Next session starts with: seed.csv with the cars already spotted (Golf GTI Rabbit Edition, Golf R, G63 AMG, G-Class Brabus Widestar, M3 Competition, F-150), a loader in core/vehicles.py, and a first `search` command.
- Commit(s): "Add vehicle catalog schema and database layer"