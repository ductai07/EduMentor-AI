# ADR 0003 - Stabilize Docker Compose Before Kubernetes

## Status

Accepted.

## Decision

Use a single VM Docker Compose deployment before Kubernetes or Helm.

## Rationale

- The current portfolio value comes from measurable production behavior, not orchestration complexity.
- Compose is enough to prove health checks, eval smoke, model gateway, cache, and backup/restore.

## Consequences

- Kubernetes is deferred until VM deployment is stable and measured.
- Deployment docs must include rollback and smoke checks.
