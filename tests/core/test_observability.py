import pytest

from core.observability import InMemorySpanRecorder, TraceContext, redact_sensitive


def test_trace_context_exports_stable_metadata():
    context = TraceContext(
        request_id="req1",
        thread_id="thread1",
        user_id="alice@example.com",
        course_id="ai101",
        model_route="edumentor-quality",
        prompt_version="prompt_v1",
        policy_version="policy_v1",
        index_version="idx_a",
    )

    metadata = context.to_metadata()

    assert metadata["request_id"] == "req1"
    assert metadata["thread_id"] == "thread1"
    assert metadata["user_hash"].startswith("user_")
    assert metadata["course_id"] == "ai101"
    assert "alice@example.com" not in metadata.values()


def test_redact_sensitive_masks_known_secret_fields():
    redacted = redact_sensitive(
        {
            "api_key": "secret",
            "Authorization": "Bearer token",
            "nested": {"password": "pw", "safe": "ok"},
        }
    )

    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["Authorization"] == "[REDACTED]"
    assert redacted["nested"]["password"] == "[REDACTED]"
    assert redacted["nested"]["safe"] == "ok"


def test_span_recorder_captures_success_with_redacted_metadata():
    recorder = InMemorySpanRecorder()

    with recorder.span("retrieval", {"api_key": "secret", "query": "logic"}) as span:
        span.set_output({"count": 3})

    assert recorder.events[0]["event"] == "start"
    assert recorder.events[0]["name"] == "retrieval"
    assert recorder.events[0]["metadata"]["api_key"] == "[REDACTED]"
    assert recorder.events[-1]["event"] == "end"
    assert recorder.events[-1]["output"] == {"count": 3}


def test_span_recorder_captures_error():
    recorder = InMemorySpanRecorder()

    with pytest.raises(ValueError):
        with recorder.span("llm"):
            raise ValueError("bad response")

    assert recorder.events[-1]["event"] == "error"
    assert recorder.events[-1]["error_type"] == "ValueError"
