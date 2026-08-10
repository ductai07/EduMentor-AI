# Observability V1

Date: 2026-08-10

## Implemented

- Trace metadata contract in `core/observability.py`.
- User identifiers are hashed before trace metadata export.
- Secret-like keys are recursively redacted.

## Trace Fields

- request_id
- thread_id
- user_hash
- course_id
- model_route
- prompt_version
- policy_version
- index_version

## Pending Runtime Wiring

- Langfuse spans for FastAPI request, LangGraph nodes, retriever, tools, and LLM calls.
- Dashboard screenshot after local/staging stack is running.
- Redacted trace export sample.
