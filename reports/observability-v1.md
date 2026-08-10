# Observability V1

Date: 2026-08-10

## Implemented

- Trace metadata contract in `core/observability.py`.
- User identifiers are hashed before trace metadata export.
- Secret-like keys are recursively redacted.
- Runtime span recorder abstraction with `NullSpanRecorder`, `InMemorySpanRecorder`, and optional `LangfuseSpanRecorder`.
- LangGraph assistant spans for retrieval, tool execution, and response generation.

## Trace Fields

- request_id
- thread_id
- user_hash
- course_id
- model_route
- prompt_version
- policy_version
- index_version

## Runtime Spans

- `retrieval`: top_k, minimum score threshold, source count.
- `tool_execution`: selected tool and output type.
- `response_generation`: route decision, grounding requirement, response length.

## Pending Runtime Evidence

- Langfuse dashboard screenshot after local/staging stack is running.
- Redacted trace export sample.
