import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    outcome: str
    reason: str


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+the\s+system\s+prompt",
    r"developer\s+message",
    r"system\s+prompt",
]

ACADEMIC_INTEGRITY_PATTERNS = [
    r"\bbai thi\b",
    r"\bexam\b",
    r"\bdap an truc tiep\b",
    r"\bgiai ho\b",
]

PII_REQUEST_PATTERNS = [
    r"\bemail\b.*\b(sinh vien|student|tat ca)\b",
    r"\bso dien thoai\b",
    r"\bphone\b.*\b(student|sinh vien)\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def evaluate_input_policy(text: str) -> PolicyDecision:
    normalized = text or ""
    if _matches_any(normalized, PROMPT_INJECTION_PATTERNS):
        return PolicyDecision(outcome="block", reason="prompt_injection")
    if _matches_any(normalized, PII_REQUEST_PATTERNS):
        return PolicyDecision(outcome="block", reason="pii_request")
    if _matches_any(normalized, ACADEMIC_INTEGRITY_PATTERNS):
        return PolicyDecision(outcome="require_approval", reason="academic_integrity")
    return PolicyDecision(outcome="allow", reason="ok")
