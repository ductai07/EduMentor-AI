# Cache Benchmark v1

Date: 2026-08-10

Scope: local synthetic retrieval benchmark for the version-aware retrieval cache. This validates cache mechanics and latency shape without requiring a live Milvus corpus.

## Setup

- Cache backend: `InMemoryJsonCache`
- Retriever path: `EnsembleRetriever.search`
- Dataset: 25 unique queries, each called twice
- Cold path: fake uncached retrieval with 8ms async delay
- Warm path: same normalized query, same `course_id`, same `index_version`

## Results

| Metric | Value |
| --- | ---: |
| Uncached calls | 25 |
| Cache hits | 25 |
| Cache misses | 25 |
| Hit rate | 50.00% |
| Cold p50 | 15.611 ms |
| Warm p50 | 0.077 ms |
| Cold p95 | 16.089 ms |
| Warm p95 | 0.646 ms |

## Interpretation

The retrieval cache avoids repeated retrieval work for identical normalized queries under the same course, retriever configuration, embedding model, and index version. Changing `index_version` creates a different cache key, so re-indexing invalidates older retrieval results.

This report does not claim production latency. The next benchmark should run against live Redis and Milvus with a real course corpus and concurrent traffic.
