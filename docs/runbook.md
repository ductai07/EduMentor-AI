# Runbook

## Provider Down

- Symptom: LLM calls fail or fallback count rises.
- Check: LiteLLM logs and provider API status.
- Action: route to `edumentor-fast` or `edumentor-local`, then run eval smoke.

## Milvus Slow

- Symptom: `/ready` may pass but `/ask` p95 rises.
- Check: Milvus container health and retrieval latency spans.
- Action: reduce `RETRIEVER_TOP_K`, inspect index version, restart Milvus only after checking ingestion jobs.

## Redis Down

- Symptom: cache hit rate drops to zero.
- Action: keep serving uncached responses, restart Redis, verify no stale key reuse.

## Unsafe Prompt Spike

- Symptom: guardrail block rate increases.
- Action: sample redacted traces, confirm policy reason distribution, add regression cases.
