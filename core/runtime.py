from dataclasses import dataclass
from typing import Any

from core.cache import JsonCacheBackend, RedisJsonCache
from core.evidence import build_index_version
from core.observability import LangfuseSpanRecorder, NullSpanRecorder, SpanRecorder


@dataclass
class RuntimeDependencies:
    cache_backend: JsonCacheBackend
    span_recorder: SpanRecorder
    index_version: str

    async def close(self) -> None:
        close = getattr(self.cache_backend, "close", None)
        if close:
            await close()


def build_runtime_dependencies(
    settings: Any,
    collection_name: str | None = None,
) -> RuntimeDependencies:
    index_version = build_index_version(
        collection_name or settings.MILVUS_COLLECTION,
        settings.EMBEDDING_MODEL,
        settings.CHUNK_SIZE,
        settings.CHUNK_OVERLAP,
    )
    cache_backend = RedisJsonCache(settings.REDIS_URL)

    if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
        span_recorder: SpanRecorder = LangfuseSpanRecorder(
            host=settings.LANGFUSE_HOST,
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
        )
    else:
        span_recorder = NullSpanRecorder()

    return RuntimeDependencies(
        cache_backend=cache_backend,
        span_recorder=span_recorder,
        index_version=index_version,
    )
