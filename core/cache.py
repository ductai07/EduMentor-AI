import hashlib
import json
import re
from typing import Any, Protocol


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", query or "").strip().lower()


def _hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def build_cache_key(
    namespace: str,
    environment: str,
    course_id: str,
    user_scope: str,
    query: str,
    index_version: str,
    embedding_model: str,
    retriever_config: str,
    model_route: str,
    prompt_version: str,
    policy_version: str,
) -> str:
    query_hash = _hash(normalize_query(query))
    dimensions = [
        f"course={course_id}",
        f"user={user_scope}",
        f"q={query_hash}",
        f"index={index_version}",
        f"embed={_hash(embedding_model, 10)}",
        f"retriever={_hash(retriever_config, 10)}",
        f"model={model_route}",
        f"prompt={prompt_version}",
        f"policy={policy_version}",
    ]
    return f"edumentor:{environment}:{namespace}:" + ":".join(dimensions)


class JsonCacheBackend(Protocol):
    async def get_json(self, key: str) -> Any | None:
        ...

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ...


class InMemoryJsonCache:
    def __init__(self) -> None:
        self._values: dict[str, str] = {}
        self.hits = 0
        self.misses = 0

    async def get_json(self, key: str) -> Any | None:
        if key not in self._values:
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(self._values[key])

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self._values[key] = json.dumps(value, ensure_ascii=False, default=str)


class RedisJsonCache:
    def __init__(self, redis_url: str) -> None:
        try:
            from redis.asyncio import from_url
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install redis to use RedisJsonCache.") from exc
        self._client = from_url(redis_url, decode_responses=True)

    async def get_json(self, key: str) -> Any | None:
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        raw = json.dumps(value, ensure_ascii=False, default=str)
        await self._client.set(key, raw, ex=ttl_seconds)

    async def close(self) -> None:
        await self._client.aclose()
