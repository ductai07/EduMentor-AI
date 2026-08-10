import hashlib
from dataclasses import dataclass
from typing import Any


SENSITIVE_KEYS = {"api_key", "authorization", "password", "secret", "token"}


def _user_hash(user_id: str | None) -> str | None:
    if not user_id:
        return None
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]
    return f"user_{digest}"


@dataclass(frozen=True)
class TraceContext:
    request_id: str
    thread_id: str | None = None
    user_id: str | None = None
    course_id: str | None = None
    model_route: str | None = None
    prompt_version: str | None = None
    policy_version: str | None = None
    index_version: str | None = None

    def to_metadata(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "thread_id": self.thread_id,
            "user_hash": _user_hash(self.user_id),
            "course_id": self.course_id,
            "model_route": self.model_route,
            "prompt_version": self.prompt_version,
            "policy_version": self.policy_version,
            "index_version": self.index_version,
        }


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value
