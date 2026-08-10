from dataclasses import dataclass, field
from typing import Any

import httpx

from core.model_policy import ModelRoute


@dataclass(frozen=True)
class LLMResult:
    content: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.http_client = http_client or httpx.AsyncClient(timeout=30.0)

    async def complete(
        self,
        messages: list[dict[str, str]],
        route: ModelRoute,
        metadata: dict[str, Any] | None = None,
    ) -> LLMResult:
        models_to_try = [route.model]
        if route.fallback_model:
            models_to_try.append(route.fallback_model)

        last_error: Exception | None = None
        for model in models_to_try:
            try:
                return await self._complete_with_model(messages, model, route.timeout_seconds, metadata)
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.TransportError, ValueError) as exc:
                last_error = exc
                continue
        if last_error:
            raise last_error
        raise RuntimeError("No model route configured")

    async def _complete_with_model(
        self,
        messages: list[dict[str, str]],
        model: str,
        timeout_seconds: float,
        metadata: dict[str, Any] | None,
    ) -> LLMResult:
        response = await self.http_client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": model, "messages": messages, "metadata": metadata or {}},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Malformed OpenAI-compatible response") from exc
        return LLMResult(
            content=content,
            model=model,
            usage=payload.get("usage", {}),
            raw=payload,
        )
