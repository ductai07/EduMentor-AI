# Phase 09 - Deployment And Operations

## Goal

Deploy a production-like VM Docker Compose stack with backups, rollback, and smoke tests.

## Files

- Create: `Dockerfile`
- Create: `ui/Dockerfile`
- Create: `infrastructure/nginx/nginx.conf`
- Create: `docs/deployment.md`
- Create: `docs/runbook.md`
- Create: `docs/postmortem-template.md`
- Create: `.github/workflows/ci.yml`
- Modify: `docker-compose.yml`
- Modify: `README.md`

## Services

- API
- UI
- MongoDB
- Redis
- Milvus stack
- LiteLLM
- Langfuse or cloud Langfuse config
- Reverse proxy

## Acceptance Gate

- Fresh VM deploy works from README.
- HTTPS, probes, backup/restore, and rollback are documented.
- Load test report includes p50/p95/error/resource usage.

## Progress

- [x] Add API Dockerfile.
- [x] Add UI Dockerfile.
- [x] Add API, UI, MongoDB, Redis, Milvus, and LiteLLM Compose services.
- [x] Add CI workflow for tests and eval smoke.
- [x] Add deployment guide, runbook, and postmortem template.
- [x] Validate Compose config.
- [ ] Run fresh VM deployment.
- [ ] Add HTTPS reverse proxy.
- [ ] Complete backup/restore and load-test reports.
