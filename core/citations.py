from typing import Any


class CitationVerificationError(ValueError):
    pass


def verify_citations(
    cited_chunk_ids: list[int],
    retrieved_sources: list[dict[str, Any]],
    expected_index_version: str | None = None,
) -> None:
    sources_by_chunk = {source.get("chunk_id"): source for source in retrieved_sources}
    for chunk_id in cited_chunk_ids:
        if chunk_id not in sources_by_chunk:
            raise CitationVerificationError(f"Unknown citation chunk: {chunk_id}")
        source = sources_by_chunk[chunk_id]
        if expected_index_version and source.get("index_version") != expected_index_version:
            raise CitationVerificationError(
                f"Citation chunk {chunk_id} uses stale index {source.get('index_version')}"
            )
