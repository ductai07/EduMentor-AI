import asyncio
from typing import Any

from langchain_core.runnables import Runnable

from core.llm_client import LLMClient
from core.model_policy import ModelRoute


ROLE_MAP = {
    "human": "user",
    "ai": "assistant",
    "system": "system",
    "chat": "user",
}


def _message_to_openai(message: Any) -> dict[str, str]:
    role = ROLE_MAP.get(getattr(message, "type", ""), getattr(message, "role", "user"))
    content = getattr(message, "content", str(message))
    return {"role": role, "content": str(content)}


def to_openai_messages(value: Any) -> list[dict[str, str]]:
    if hasattr(value, "to_messages"):
        return [_message_to_openai(message) for message in value.to_messages()]
    if isinstance(value, list):
        return [
            message if isinstance(message, dict) else _message_to_openai(message)
            for message in value
        ]
    if isinstance(value, dict) and {"role", "content"} <= set(value):
        return [{"role": str(value["role"]), "content": str(value["content"])}]
    return [{"role": "user", "content": str(value)}]


class LLMGatewayRunnable(Runnable[Any, str]):
    def __init__(
        self,
        client: LLMClient,
        route: ModelRoute,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.client = client
        self.route = route
        self.metadata = metadata or {}

    def invoke(self, input: Any, config: Any | None = None, **kwargs: Any) -> str:
        return asyncio.run(self.ainvoke(input, config=config, **kwargs))

    async def ainvoke(self, input: Any, config: Any | None = None, **kwargs: Any) -> str:
        result = await self.client.complete(
            messages=to_openai_messages(input),
            route=self.route,
            metadata=self.metadata,
        )
        return result.content
