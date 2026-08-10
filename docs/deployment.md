# Deployment Guide

## Target

Production-like single VM deployment with Docker Compose before Kubernetes.

## Prerequisites

- Docker and Docker Compose.
- `.env` created from `.env.example`.
- Strong `JWT_SECRET_KEY` for staging/production.
- `CORS_ALLOW_ORIGINS` set to explicit HTTPS origins in staging/production.

## Commands

```powershell
docker compose up -d
docker compose ps
```

## Smoke Checks

```powershell
curl http://localhost:5000/health
curl http://localhost:5000/ready
python -m evals.run_eval --dataset evals/datasets/edumentor_v1.jsonl --output reports/eval-baseline-v1.json
```

## Rollback

1. Keep previous image tag.
2. Stop current API/UI containers.
3. Start previous image tag.
4. Run `/health`, `/ready`, and eval smoke.

## Not Yet Claimed

- HTTPS reverse proxy is not wired in this slice.
- Backup/restore drill is not complete.
- Load test report is not complete.
