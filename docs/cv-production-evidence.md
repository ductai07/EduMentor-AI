# CV Production Evidence

Use this document as the interview-facing proof map for EduMentor AI.

## Strong CV Bullets

- Built a production-style educational RAG assistant with FastAPI, React, LangGraph, Milvus, MongoDB, Redis, and LiteLLM.
- Implemented versioned evidence IDs for document, chunk, and index lineage to reduce stale citation risk.
- Routed LLM calls through an OpenAI-compatible LiteLLM gateway with logical model routes and fallback policy.
- Added deterministic guardrails for prompt injection, PII exfiltration, academic-integrity approval, tool allowlists, timeouts, and output-size limits.
- Built an offline RAG evaluation harness with Recall, MRR, nDCG, and citation-oriented reporting.
- Added version-aware retrieval caching keyed by course/user scope, index version, embedding model, and retriever configuration.
- Added runtime observability spans for retrieval, tool execution, and response generation with secret redaction and optional Langfuse integration.
- Hardened Docker Compose deployment with health checks, restart policies, CI pytest/eval smoke, Compose validation, and Docker build gates.

## Interview Architecture Story

1. Documents are uploaded, parsed, chunked, embedded, and indexed into Milvus with stable metadata.
2. Questions enter FastAPI, pass deterministic policy checks, and route through LangGraph.
3. Retrieval uses hybrid vector/BM25, reranking, score thresholding, retries, and version-aware caching.
4. Model calls go through LiteLLM, not direct provider SDKs, so provider changes are configuration-driven.
5. Tools execute behind a registry policy with allowlist, timeout, and output-size controls.
6. Responses attach normalized evidence references and produce trace metadata/spans for debugging.
7. CI runs tests, eval smoke, Compose validation, and container build gates.

## Honest Current Gaps

- Live Langfuse dashboard screenshot is pending until the stack or cloud project is configured.
- Eval dataset is still a smoke dataset; a real course benchmark needs 80-120 reviewed examples.
- Fresh VM deploy, HTTPS, backup/restore, and load-test reports still need a real target environment.
- Full ingestion orchestration with Airflow/Prefect is not implemented yet; indexing is app/script driven.
