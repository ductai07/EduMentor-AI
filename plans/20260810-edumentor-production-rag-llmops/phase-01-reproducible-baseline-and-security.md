# Phase 01 - Reproducible Baseline And Security

## Goal

Make the API start with validated production config, safe CORS, request IDs, health/readiness endpoints, and a test baseline.

## Files

- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `tests/test_config.py`
- Create: `tests/test_health.py`
- Modify: `config/settings.py`
- Modify: `api/main.py`
- Modify: `api/routes/health.py`
- Modify: `.gitignore`

## Interfaces

- `config.settings.get_settings() -> AppSettings`
- `config.settings.validate_production_settings(settings: AppSettings) -> None`
- `GET /health` returns liveness.
- `GET /ready` returns dependency readiness with MongoDB and Milvus status.
- `X-Request-ID` response header is present.

## Steps

- [x] Write failing tests for production secret validation and CORS allowlist parsing.
- [x] Run `python -m pytest tests/test_config.py -q` and confirm expected failure.
- [x] Implement typed settings and production validation.
- [x] Run `python -m pytest tests/test_config.py -q`.
- [x] Write failing tests for `/health`, `/ready`, and request ID header.
- [x] Run `python -m pytest tests/test_health.py -q` and confirm expected failure.
- [x] Implement health/readiness and request ID middleware.
- [x] Run targeted tests.
- [x] Run full Python tests available in repo.
- [ ] Commit source and test changes.

## Acceptance Gate

- Production mode rejects default JWT secret.
- CORS no longer uses wildcard by default in production.
- Health is app-only; readiness checks dependencies.
- Tests pass in a clean local Python environment.
