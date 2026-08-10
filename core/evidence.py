import hashlib
import json
import os
import re
from typing import Any


DEFAULT_COURSE_ID = "default"
DEFAULT_POLICY_VERSION = "policy_v1"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def content_hash(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _short_hash(value: str, prefix: str, length: int = 16) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"


def build_document_id(course_id: str, filename: str, document_hash: str) -> str:
    key = f"{course_id}:{filename.lower()}:{document_hash}"
    return _short_hash(key, "doc")


def build_chunk_id(document_id: str, start_index: int, text: str) -> int:
    key = f"{document_id}:{start_index}:{content_hash(text)}"
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:15], 16)


def build_index_version(
    collection_name: str,
    embedding_model: str,
    chunk_size: int,
    chunk_overlap: int,
    policy_version: str = DEFAULT_POLICY_VERSION,
) -> str:
    key = f"{collection_name}:{embedding_model}:{chunk_size}:{chunk_overlap}:{policy_version}"
    return _short_hash(key, "idx", length=12)


def ensure_evidence_metadata(
    metadata: dict[str, Any] | None,
    source_path: str,
    document_text: str,
    chunk_text: str,
    start_index: int,
    index_version: str,
) -> dict[str, Any]:
    enriched = dict(metadata or {})
    source_file = enriched.get("source_file") or enriched.get("filename") or os.path.basename(source_path)
    course_id = enriched.get("course_id") or DEFAULT_COURSE_ID
    document_hash = enriched.get("document_hash") or content_hash(document_text)
    document_id = enriched.get("document_id") or build_document_id(course_id, source_file, document_hash)
    document_version = enriched.get("document_version") or f"docv_{document_hash[:12]}"
    chunk_id = enriched.get("chunk_id") or build_chunk_id(document_id, start_index, chunk_text)

    enriched.update(
        {
            "course_id": course_id,
            "source_file": source_file,
            "document_hash": document_hash,
            "document_id": document_id,
            "document_version": document_version,
            "chunk_id": chunk_id,
            "index_version": index_version,
            "start_index": start_index,
        }
    )
    return enriched


def parse_metadata(metadata: dict[str, Any] | str | None) -> dict[str, Any]:
    if isinstance(metadata, dict):
        return metadata
    if not metadata:
        return {}
    try:
        parsed = json.loads(metadata)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def normalize_retrieved_evidence(
    text: str,
    score: float,
    sources: list[str],
    metadata: dict[str, Any] | str | None,
    title: str | None = None,
) -> dict[str, Any]:
    parsed_metadata = parse_metadata(metadata)
    return {
        "text": text,
        "score": score,
        "source": ", ".join(sources),
        "sources": sources,
        "metadata": parsed_metadata,
        "title": title or parsed_metadata.get("title", "N/A"),
        "document_id": parsed_metadata.get("document_id"),
        "chunk_id": parsed_metadata.get("chunk_id"),
        "document_version": parsed_metadata.get("document_version"),
        "index_version": parsed_metadata.get("index_version"),
        "source_file": parsed_metadata.get("source_file") or parsed_metadata.get("filename"),
        "page_number": parsed_metadata.get("page_number"),
        "slide_number": parsed_metadata.get("slide_number"),
        "timestamp": parsed_metadata.get("timestamp"),
    }
