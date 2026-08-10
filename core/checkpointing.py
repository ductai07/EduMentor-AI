import hashlib
from dataclasses import dataclass
from typing import Any


def build_thread_id(user_id: str, session_id: str) -> str:
    digest = hashlib.sha256(f"{user_id}:{session_id}".encode("utf-8")).hexdigest()[:16]
    return f"thread_{digest}"


@dataclass(frozen=True)
class ThreadCheckpoint:
    thread_id: str
    state: dict[str, Any]
    status: str
    resume_token: str | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "state": self.state,
            "status": self.status,
            "resume_token": self.resume_token,
        }
