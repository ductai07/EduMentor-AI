import hashlib
import re


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
