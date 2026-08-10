# Repository Structure

This repository keeps the current import layout stable while separating source code, runtime artifacts, plans, and operational docs.

## Runtime Source

- `api/` - FastAPI app, routers, dependencies, and app state.
- `auth/` - JWT, password hashing, auth models, and MongoDB user helpers.
- `config/` - environment-driven settings.
- `core/` - LangGraph assistant orchestration and production boundaries.
- `indexing/` - document extraction, chunking, embedding, and Milvus indexing.
- `retrievers/` - hybrid vector/BM25 retrieval.
- `tools/` - learning tools used by the assistant.
- `utils/` - shared helpers.
- `main.py` - local API launcher.

## Frontend

- `ui/` - React/Vite frontend.

## Product And Operations Artifacts

- `plans/` - implementation plans and phase checklists.
- `docs/` - architecture, deployment, runbooks, ADRs, and repository guidance.
- `reports/` - generated evaluation, load, observability, and final portfolio reports.
- `artifacts/generated/` - generated text/CSV outputs kept for reference.
- `artifacts/local-state/` - local JSON state files from prototype workflows.
- `notebooks/` - exploratory notebooks.
- `scripts/admin/` - operator/admin scripts.
- `scripts/diagnostics/` - local diagnostic scripts.

## Current Cleanup Rule

Do not move runtime packages into a deeper `src/` layout until Phase 01 creates a passing test baseline. The app currently imports packages such as `api`, `core`, and `config` from the repository root, so package migration should be a separate tested refactor.
