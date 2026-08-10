# Phase 03 - Evaluation First RAG

## Goal

Create a versioned offline RAG evaluation harness before tuning retrieval or model behavior.

## Files

- Create: `evals/datasets/edumentor_v1.jsonl`
- Create: `evals/metrics.py`
- Create: `evals/retrieval_eval.py`
- Create: `evals/answer_eval.py`
- Create: `evals/run_eval.py`
- Create: `reports/eval-baseline-v1.md`
- Create: `tests/evals/test_metrics.py`

## Metrics

- Retrieval: Recall@5, Recall@10, MRR, nDCG@10.
- Answer: groundedness, citation precision, citation recall, no-answer accuracy.
- Agent: intent accuracy and tool-selection accuracy.

## Steps

- [ ] Write tests for metric functions.
- [ ] Implement metrics.
- [ ] Add minimal dataset first, then expand to 80-120 rows.
- [ ] Add retrieval eval runner.
- [ ] Add answer eval runner with pinned judge prompt/model metadata.
- [ ] Generate baseline report.
- [ ] Commit phase.

## Acceptance Gate

- Smoke eval runs in CI without network LLM calls.
- Full eval can run manually with provider credentials.
- Report includes raw output paths and 10 failure cases.

