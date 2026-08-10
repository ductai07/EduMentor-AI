# Phase 00A - Repository Structure Cleanup

## Goal

Clean repository layout before production feature work without breaking the current top-level Python import layout.

## Files

- Create: `docs/repository-structure.md`
- Create: package markers in `api/`, `auth/`, `config/`, `core/`, `indexing/`, `retrievers/`, `utils/`, and `tests/`
- Move: generated root outputs into `artifacts/generated/`
- Move: prototype local JSON state into `artifacts/local-state/`
- Move: exploratory notebook into `notebooks/`
- Move: admin and diagnostic scripts into `scripts/`
- Modify: `.gitignore`

## Constraints

- Do not move `api/`, `core/`, `config/`, `tools/`, `indexing/`, or `retrievers/` under `src/` yet.
- Keep `main.py` at repository root until the API launch path has tests.
- Keep `data/` and `uploads/` in place during this cleanup so the existing demo path is not broken.

## Steps

- [x] Create clean artifact, script, docs, tests, and notebook folders.
- [x] Move root prototype outputs and diagnostics into those folders.
- [x] Add package markers for backend modules.
- [x] Document the repository structure.
- [x] Run syntax verification.
- [ ] Commit cleanup with `chore: clean repository structure`.

## Acceptance Gate

- Python source still parses.
- `git status --short` shows only expected moves/additions.
- Repository structure has a documented rule for future `src/` migration.
