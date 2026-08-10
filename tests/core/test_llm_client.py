import pytest
import httpx

from core.llm_client import LLMClient
from core.model_policy import ModelRoute


@pytest.mark.asyncio
async def test_llm_client_returns_openai_compatible_content():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "hello"}}], "usage": {"total_tokens": 3}},
        )

    client = LLMClient(
        base_url="https://llm.test/v1",
        api_key="test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await client.complete(
        messages=[{"role": "user", "content": "hi"}],
        route=ModelRoute(name="edumentor-fast", model="fast-model"),
    )

    assert result.content == "hello"
    assert result.model == "fast-model"
    assert result.usage == {"total_tokens": 3}


@pytest.mark.asyncio
async def test_llm_client_uses_fallback_after_provider_error():
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read().decode("utf-8")
        calls.append(payload)
        if len(calls) == 1:
            return httpx.Response(429, json={"error": "rate limited"})
        return httpx.Response(200, json={"choices": [{"message": {"content": "fallback ok"}}]})

    client = LLMClient(
        base_url="https://llm.test/v1",
        api_key="test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await client.complete(
        messages=[{"role": "user", "content": "hi"}],
        route=ModelRoute(name="edumentor-quality", model="quality-model", fallback_model="fast-model"),
    )

    assert result.content == "fallback ok"
    assert len(calls) == 2
    assert "quality-model" in calls[0]
    assert "fast-model" in calls[1]
