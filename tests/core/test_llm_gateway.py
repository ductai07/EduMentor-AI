from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import pytest

from core.llm_client import LLMResult
from core.llm_gateway import LLMGatewayRunnable
from core.model_policy import ModelRoute


class FakeLLMClient:
    def __init__(self) -> None:
        self.calls = []

    async def complete(self, messages, route, metadata=None):
        self.calls.append({"messages": messages, "route": route, "metadata": metadata})
        return LLMResult(content="gateway ok", model=route.model)


@pytest.mark.asyncio
async def test_llm_gateway_runnable_uses_openai_messages_and_route():
    client = FakeLLMClient()
    route = ModelRoute(name="edumentor-fast", model="edumentor-fast")
    llm = LLMGatewayRunnable(client=client, route=route, metadata={"node": "intent"})
    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are concise."), ("human", "Question: {question}")]
    )

    result = await (prompt | llm | StrOutputParser()).ainvoke({"question": "hi"})

    assert result == "gateway ok"
    assert client.calls[0]["route"] == route
    assert client.calls[0]["metadata"] == {"node": "intent"}
    assert client.calls[0]["messages"] == [
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "Question: hi"},
    ]
