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

