# Demo Script

## 1. Problem

EduMentor answers learning questions over course documents and creates study artifacts such as summaries, quizzes, flashcards, and study plans.

## 2. Production Proof

Show:

- `docs/architecture.md`
- `plans/20260810-edumentor-production-rag-llmops/`
- `python -m pytest -q`
- `python -m evals.run_eval --dataset evals/datasets/edumentor_v1.jsonl --output reports/eval-baseline-v1.json`
- `docker compose config`

## 3. Engineering Story

Explain:

- Why evidence versioning came before cache.
- Why LiteLLM boundary came before provider swapping.
- Why deterministic guardrails run before LLM judge.
- Why Compose is the first deployment target before Kubernetes.

## 4. Honest Boundary

Do not claim full production deployment until fresh VM deploy, dashboard capture, full eval, and backup/restore drill are complete.
