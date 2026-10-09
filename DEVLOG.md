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
- Next session starts with:
- Commit(s):
