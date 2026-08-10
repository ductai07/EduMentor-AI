from types import MethodType

import pytest

from core.cache import InMemoryJsonCache
from retrievers.ensemble_retriever import EnsembleRetriever


def make_retriever(cache):
    retriever = object.__new__(EnsembleRetriever)
    retriever.collection_name = "course_docs"
    retriever.model_name = "embed-v1"
    retriever.vector_weight = 0.7
    retriever.bm25_weight = 0.3
    retriever.top_k = 3
    retriever.cache_backend = cache
    retriever.index_version = "idx-v1"
    retriever.cache_ttl_seconds = 60
    return retriever


@pytest.mark.asyncio
async def test_retrieval_cache_returns_cached_result_for_same_versioned_key():
    cache = InMemoryJsonCache()
    retriever = make_retriever(cache)
    calls = {"count": 0}

    async def fake_uncached(self, query, effective_top_k, filter_metadata):
        calls["count"] += 1
        return [{"text": f"{query}:{effective_top_k}", "score": 0.9}]

    retriever._search_uncached = MethodType(fake_uncached, retriever)

    first = await retriever.search("Logic menh de", top_k=2, filter_metadata={"course_id": "logic"})
    second = await retriever.search(" logic   menh de ", top_k=2, filter_metadata={"course_id": "logic"})

    assert first == second
    assert calls["count"] == 1
    assert cache.hits == 1


@pytest.mark.asyncio
async def test_retrieval_cache_invalidates_when_index_version_changes():
    cache = InMemoryJsonCache()
    retriever = make_retriever(cache)
    calls = {"count": 0}

    async def fake_uncached(self, query, effective_top_k, filter_metadata):
        calls["count"] += 1
        return [{"text": f"version:{self.index_version}", "score": 0.9}]

    retriever._search_uncached = MethodType(fake_uncached, retriever)

    first = await retriever.search("cache me", top_k=2)
    retriever.index_version = "idx-v2"
    second = await retriever.search("cache me", top_k=2)

    assert first != second
    assert calls["count"] == 2
