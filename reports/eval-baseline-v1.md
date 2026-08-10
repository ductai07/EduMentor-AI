# Eval Baseline V1

Date: 2026-08-10

## Dataset

- Path: `evals/datasets/edumentor_v1.jsonl`
- Initial smoke size: 3 examples
- Categories covered: single_chunk, no_answer

## Current Status

This is the smoke baseline for wiring the offline evaluation harness. Full 80-120 sample coverage will be expanded after the evidence contract and ingestion path are stable against real course documents.

## Commands

```powershell
python -m pytest tests/evals/test_metrics.py -q
python -m evals.run_eval --dataset evals/datasets/edumentor_v1.jsonl --output reports/eval-baseline-v1.json
```

## Metrics

The initial command uses empty predictions unless `reports/raw/retrieval_predictions.json` exists. Empty-prediction metrics are expected to be zero and act as the first regression floor.
