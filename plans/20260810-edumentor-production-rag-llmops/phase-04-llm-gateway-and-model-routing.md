# Phase 04 - LLM Gateway And Model Routing

## Goal

Remove direct provider coupling from LangGraph and route through an OpenAI-compatible LiteLLM boundary.

## Files

- Create: `core/llm_client.py`
- Create: `core/llm_gateway.py`
- Create: `core/model_policy.py`
- Create: `infrastructure/litellm/config.yaml`
- Create: `tests/core/test_model_policy.py`
- Create: `tests/core/test_llm_client.py`
- Create: `tests/core/test_llm_gateway.py`
- Modify: `core/learning_assistant_v2.py`
- Modify: `docker-compose.yml`
- Modify: `.env.example`

## Interfaces

- `LLMClient.ainvoke(messages, route, metadata) -> str | dict`
- `select_model_route(task_type, requires_grounding, user_tier) -> ModelRoute`
- Logical routes: `edumentor-fast`, `edumentor-quality`, `edumentor-local`.

## Steps

- [x] Write policy tests for route selection.
- [x] Implement minimal route policy.
- [x] Write client tests for timeout/fallback using fake transport.
- [x] Implement OpenAI-compatible async client wrapper.
- [x] Replace direct `GoogleGenerativeAI` use in graph nodes.
- [x] Add LiteLLM config and Compose service.
- [ ] Run eval comparison report.
- [x] Commit phase.

## Acceptance Gate

- Changing provider requires config only.
- Timeout, 429, 5xx, malformed response are tested.
- Eval report compares at least two logical models.
