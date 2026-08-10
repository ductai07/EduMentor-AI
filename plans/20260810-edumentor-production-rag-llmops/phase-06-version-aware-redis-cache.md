# Phase 06 - Version Aware Redis Cache

## Goal

Reduce latency/cost without returning stale or cross-user data.

## Files

- Create: `core/cache.py`
- Create: `tests/core/test_cache_keys.py`
- Modify: `retrievers/ensemble_retriever.py`
- Modify: `tools/*.py` only where pure/idempotent caching is safe.
- Modify: `docker-compose.yml`
- Modify: `.env.example`

## Cache Order

1. Embedding cache.
2. Retrieval result cache.
3. Pure tool-output cache.
4. Answer cache only after scope/invalidation is proven.

## Cache Key Required Parts

- environment
- course/user scope
- normalized query hash
- index version
- embedding model
- retriever config
- model route
- prompt version
- policy version

## Acceptance Gate

- No cross-course or cross-user leakage.
- Re-index invalidates old retrieval results.
- Report includes hit rate, p50/p95, and token/cost delta.

## Progress

- [x] Add version-aware cache key builder.
- [x] Test course/user/index isolation.
- [x] Add Redis service and `REDIS_URL` config.
- [x] Wire retrieval-result cache into retriever.
- [x] Add benchmark report with hit rate and p50/p95 delta.
