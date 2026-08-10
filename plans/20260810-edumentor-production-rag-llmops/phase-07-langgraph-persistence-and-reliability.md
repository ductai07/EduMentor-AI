# Phase 07 - LangGraph Persistence And Reliability

## Goal

Make workflows restart-safe and failure-aware.

## Files

- Create: `core/checkpointing.py`
- Create: `tests/core/test_checkpointing.py`
- Create: `tests/integration/test_failure_modes.py`
- Modify: `core/learning_assistant_v2.py`
- Modify: `api/routes/chat.py`

## Steps

- [x] Add thread ID contract.
- [ ] Add LangGraph checkpointer.
- [x] Test pause/resume.
- [ ] Test restart recovery.
- [ ] Add bounded retries for transient failures.
- [ ] Add no-answer threshold.
- [ ] Commit phase.

## Acceptance Gate

- Restart does not lose approved workflow state.
- Provider down, Redis down, Milvus slow, and worker restart are handled with documented degradation.
