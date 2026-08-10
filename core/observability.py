import hashlib
from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Iterator


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


@dataclass
class SpanHandle:
    name: str
    recorder: "SpanRecorder"
    metadata: dict[str, Any] = field(default_factory=dict)
    output: Any | None = None

    def set_output(self, output: Any) -> None:
        self.output = redact_sensitive(output)


class SpanRecorder:
    @contextmanager
    def span(self, name: str, metadata: dict[str, Any] | None = None) -> Iterator[SpanHandle]:
        handle = SpanHandle(name=name, recorder=self, metadata=redact_sensitive(metadata or {}))
        start = perf_counter()
        self.on_start(handle)
        try:
            yield handle
        except Exception as exc:
            self.on_error(handle, exc, duration_ms=(perf_counter() - start) * 1000)
            raise
        else:
            self.on_end(handle, duration_ms=(perf_counter() - start) * 1000)

    def on_start(self, handle: SpanHandle) -> None:
        return None

    def on_end(self, handle: SpanHandle, duration_ms: float) -> None:
        return None

    def on_error(self, handle: SpanHandle, exc: Exception, duration_ms: float) -> None:
        return None


class NullSpanRecorder(SpanRecorder):
    pass


class InMemorySpanRecorder(SpanRecorder):
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def on_start(self, handle: SpanHandle) -> None:
        self.events.append({"event": "start", "name": handle.name, "metadata": handle.metadata})

    def on_end(self, handle: SpanHandle, duration_ms: float) -> None:
        self.events.append(
            {
                "event": "end",
                "name": handle.name,
                "duration_ms": duration_ms,
                "output": handle.output,
            }
        )

    def on_error(self, handle: SpanHandle, exc: Exception, duration_ms: float) -> None:
        self.events.append(
            {
                "event": "error",
                "name": handle.name,
                "duration_ms": duration_ms,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )


class LangfuseSpanRecorder(SpanRecorder):
    def __init__(self, host: str | None = None, public_key: str | None = None, secret_key: str | None = None) -> None:
        try:
            from langfuse import Langfuse
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install langfuse to use LangfuseSpanRecorder.") from exc
        self._client = Langfuse(host=host, public_key=public_key, secret_key=secret_key)
        self._active: dict[int, Any] = {}

    def on_start(self, handle: SpanHandle) -> None:
        span = self._client.span(name=handle.name, metadata=handle.metadata)
        self._active[id(handle)] = span

    def on_end(self, handle: SpanHandle, duration_ms: float) -> None:
        span = self._active.pop(id(handle), None)
        if span:
            span.update(output=handle.output, metadata={**handle.metadata, "duration_ms": duration_ms})
            span.end()

    def on_error(self, handle: SpanHandle, exc: Exception, duration_ms: float) -> None:
        span = self._active.pop(id(handle), None)
        if span:
            span.update(
                level="ERROR",
                status_message=str(exc),
                metadata={**handle.metadata, "duration_ms": duration_ms, "error_type": type(exc).__name__},
            )
            span.end()
