from types import SimpleNamespace

import pytest

from core.cache import InMemoryJsonCache, RedisJsonCache
from core.evidence import build_index_version
from core.observability import NullSpanRecorder


def make_settings(**overrides):
    values = {
        "MILVUS_COLLECTION": "course_docs",
        "EMBEDDING_MODEL": "embed-v1",
        "CHUNK_SIZE": 500,
        "CHUNK_OVERLAP": 50,
        "REDIS_URL": "redis://redis:6379/0",
        "LANGFUSE_HOST": None,
        "LANGFUSE_PUBLIC_KEY": None,
        "LANGFUSE_SECRET_KEY": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_runtime_dependencies_share_index_version_with_redis_cache():
    from core.runtime import build_runtime_dependencies

    runtime = build_runtime_dependencies(make_settings())

    assert isinstance(runtime.cache_backend, RedisJsonCache)
    assert isinstance(runtime.span_recorder, NullSpanRecorder)
    assert runtime.index_version == build_index_version(
        "course_docs",
        "embed-v1",
        500,
        50,
    )


def test_runtime_dependencies_use_active_collection_override():
    from core.runtime import build_runtime_dependencies

    runtime = build_runtime_dependencies(make_settings(), collection_name="tenant_docs")

    assert runtime.index_version == build_index_version(
        "tenant_docs",
        "embed-v1",
        500,
        50,
    )


def test_learning_assistant_passes_cache_and_index_version_to_retriever(monkeypatch):
    import core.learning_assistant_v2 as assistant_module

    captured = {}

    class FakeRetriever:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(assistant_module, "EnsembleRetriever", FakeRetriever)
    monkeypatch.setattr(assistant_module.LearningAssistant, "_register_default_tools", lambda self: None)
    monkeypatch.setattr(assistant_module.LearningAssistant, "_setup_workflow", lambda self: object())
    monkeypatch.setattr(assistant_module, "ToolRegistry", lambda assistant: object())

    cache = InMemoryJsonCache()
    assistant_module.LearningAssistant(
        mongo_collection=None,
        llm_client=object(),
        cache_backend=cache,
        index_version="idx-current",
    )

    assert captured["cache_backend"] is cache
    assert captured["index_version"] == "idx-current"


@pytest.mark.asyncio
async def test_source_formatter_rejects_stale_index_evidence():
    from core.learning_assistant_v2 import LearningAssistant

    assistant = object.__new__(LearningAssistant)
    assistant.retriever = SimpleNamespace(index_version="idx-current")

    result = await assistant._format_sources_node(
        {
            "response": "An answer",
            "sources": [
                {
                    "chunk_id": 123,
                    "source_file": "lesson.pdf",
                    "document_version": "docv-1",
                    "index_version": "idx-old",
                    "metadata": {},
                }
            ],
            "route_decision": "RAG",
            "selected_tool_name": None,
        }
    )

    assert result["sources"] == []
    assert result["response"] == "Unable to verify sources for this response."


@pytest.mark.asyncio
async def test_source_formatter_rejects_evidence_without_chunk_id():
    from core.learning_assistant_v2 import LearningAssistant

    assistant = object.__new__(LearningAssistant)
    assistant.retriever = SimpleNamespace(index_version="idx-current")

    result = await assistant._format_sources_node(
        {
            "response": "An answer",
            "sources": [
                {
                    "source_file": "lesson.pdf",
                    "document_version": "docv-1",
                    "index_version": "idx-current",
                    "metadata": {},
                }
            ],
            "route_decision": "RAG",
            "selected_tool_name": None,
        }
    )

    assert result["sources"] == []
    assert result["response"] == "Unable to verify sources for this response."
