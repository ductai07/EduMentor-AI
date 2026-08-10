# Phase 05 - Deterministic Guardrails And Citation Verification

## Goal

Add layered safety gates for input, retrieval, tools, output, and academic integrity.

## Files

- Create: `core/policy.py`
- Create: `core/citations.py`
- Create: `tests/core/test_policy.py`
- Create: `tests/core/test_citations.py`
- Modify: `core/learning_assistant_v2.py`
- Modify: `tools/tool_registry.py`

## Policy Outcomes

- `allow`
- `block`
- `require_approval`

## Steps

- [x] Write tests for prompt injection, PII, cross-course access, and exam-answer requests.
- [x] Implement deterministic policy checks.
- [x] Write citation verifier tests for invalid IDs and stale versions.
- [x] Implement citation verification before final output.
- [ ] Add tool allowlist, timeout, and output-size checks.
- [ ] Commit phase.

## Acceptance Gate

- Unsafe inputs fail closed.
- Citation spoofing is rejected.
- Sensitive tools do not execute without approval.
