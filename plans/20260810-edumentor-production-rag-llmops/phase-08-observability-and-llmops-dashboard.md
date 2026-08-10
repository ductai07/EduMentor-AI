# Phase 08 - Observability And LLMOps Dashboard

## Goal

Trace every answer end-to-end and measure latency, tokens, cost, cache, fallback, and guardrails.

## Files

- Create: `core/observability.py`
- Create: `infrastructure/langfuse/docker-compose.yml`
- Create: `reports/observability-v1.md`
- Modify: `api/main.py`
- Modify: `core/learning_assistant_v2.py`
- Modify: `retrievers/ensemble_retriever.py`

## Trace Fields

- request_id
- trace_id
- thread_id
- user_hash
- course_id
- model_route/model_name
- prompt_version
- policy_version
- index_version
- token counts and estimated cost

## Acceptance Gate

- A single response can be traced through API, graph, retrieval, tool, LLM, and output guardrail.
- Trace redaction prevents secrets and raw PII leaks.
- Dashboard screenshot and runbook exist.

## Progress

- [x] Add trace metadata contract.
- [x] Add user hashing and recursive secret redaction tests.
- [x] Add `reports/observability-v1.md` skeleton.
- [ ] Wire Langfuse/OpenTelemetry runtime spans.
- [ ] Capture dashboard screenshot after stack is running.
