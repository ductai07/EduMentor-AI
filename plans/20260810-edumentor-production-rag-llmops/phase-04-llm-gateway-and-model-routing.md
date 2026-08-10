# Phase 04 - LLM Gateway And Model Routing

## Goal

Remove direct provider coupling from LangGraph and route through an OpenAI-compatible LiteLLM boundary.

## Files

- Create: `core/llm_client.py`
- Create: `core/model_policy.py`
- Create: `infrastructure/litellm/config.yaml`
- Create: `tests/core/test_model_policy.py`
- Create: `tests/core/test_llm_client.py`
- Modify: `core/learning_assistant_v2.py`
- Modify: `docker-compose.yml`
- Modify: `.env.example`

## Interfaces

- `LLMClient.ainvoke(messages, route, metadata) -> str | dict`
- `select_model_route(task_type, requires_grounding, user_tier) -> ModelRoute`
- Logical routes: `edumentor-fast`, `edumentor-quality`, `edumentor-local`.

## Steps

- [ ] Write policy tests for route selection.
- [ ] Implement minimal route policy.
- [ ] Write client tests for timeout/fallback using fake transport.
- [ ] Implement OpenAI-compatible async client wrapper.
- [ ] Replace direct `GoogleGenerativeAI` use in graph nodes.
- [ ] Add LiteLLM config and Compose service.
- [ ] Run eval comparison report.
- [ ] Commit phase.

## Acceptance Gate

- Changing provider requires config only.
- Timeout, 429, 5xx, malformed response are tested.
- Eval report compares at least two logical models.

