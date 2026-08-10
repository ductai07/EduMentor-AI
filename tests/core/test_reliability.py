import pytest

from core.reliability import filter_sources_by_score, has_confident_source, retry_async


@pytest.mark.asyncio
async def test_retry_async_retries_transient_failure():
    calls = {"count": 0}

    async def flaky():
        calls["count"] += 1
        if calls["count"] == 1:
            raise TimeoutError("slow provider")
        return "ok"

    assert await retry_async(flaky, attempts=2, backoff_seconds=0) == "ok"
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_retry_async_stops_after_attempt_limit():
    async def always_fails():
        raise TimeoutError("still slow")

    with pytest.raises(TimeoutError):
        await retry_async(always_fails, attempts=2, backoff_seconds=0)


def test_no_answer_threshold_requires_confident_source():
    sources = [{"score": 0.2}, {"score": 0.49}]

    assert not has_confident_source(sources, min_score=0.5)
    assert filter_sources_by_score(sources, min_score=0.5) == []


def test_no_answer_threshold_keeps_confident_sources():
    sources = [{"score": 0.2}, {"score": 0.8}]

    assert has_confident_source(sources, min_score=0.5)
    assert filter_sources_by_score(sources, min_score=0.5) == [{"score": 0.8}]
