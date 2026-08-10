from core.evidence import (
    build_chunk_id,
    build_document_id,
    build_index_version,
    content_hash,
    ensure_evidence_metadata,
    format_source_references,
    normalize_retrieved_evidence,
)


def test_content_hash_is_stable_for_same_text():
    assert content_hash("  Hello\nworld  ") == content_hash("Hello world")


def test_document_id_changes_by_course_filename_and_content():
    first = build_document_id("course-a", "lesson.pdf", "hash-1")
    same = build_document_id("course-a", "lesson.pdf", "hash-1")
    other_course = build_document_id("course-b", "lesson.pdf", "hash-1")

    assert first == same
    assert first != other_course
    assert first.startswith("doc_")


def test_chunk_id_is_stable_int64_safe():
    chunk_id = build_chunk_id("doc_abc", 42, "chunk text")

    assert chunk_id == build_chunk_id("doc_abc", 42, "chunk text")
    assert isinstance(chunk_id, int)
    assert 0 < chunk_id < 2**63


def test_index_version_changes_when_retriever_config_changes():
    first = build_index_version("learning_docs", "all-MiniLM-L6-v2", 500, 50)
    changed = build_index_version("learning_docs", "all-MiniLM-L6-v2", 800, 80)

    assert first != changed
    assert first.startswith("idx_")


def test_ensure_evidence_metadata_adds_required_fields():
    metadata = ensure_evidence_metadata(
        metadata={"title": "Intro", "course_id": "ai101"},
        source_path="slides/intro.pdf",
        document_text="Artificial intelligence intro",
        chunk_text="Artificial intelligence",
        start_index=0,
        index_version="idx_test",
    )

    assert metadata["course_id"] == "ai101"
    assert metadata["source_file"] == "intro.pdf"
    assert metadata["document_id"].startswith("doc_")
    assert metadata["chunk_id"] == build_chunk_id(metadata["document_id"], 0, "Artificial intelligence")
    assert metadata["document_version"].startswith("docv_")
    assert metadata["index_version"] == "idx_test"


def test_normalize_retrieved_evidence_exposes_contract_fields():
    result = normalize_retrieved_evidence(
        text="Chunk",
        score=0.9,
        sources=["vector", "bm25"],
        metadata='{"document_id":"doc_a","chunk_id":123,"document_version":"docv_a","index_version":"idx_a","source_file":"intro.pdf","page_number":2}',
        title="Intro",
    )

    assert result["metadata"]["document_id"] == "doc_a"
    assert result["document_id"] == "doc_a"
    assert result["chunk_id"] == 123
    assert result["document_version"] == "docv_a"
    assert result["index_version"] == "idx_a"
    assert result["source_file"] == "intro.pdf"
    assert result["page_number"] == 2
    assert result["source"] == "vector, bm25"


def test_format_source_references_includes_evidence_ids():
    sources = [
        {
            "source_file": "intro.pdf",
            "chunk_id": 123,
            "document_version": "docv_a",
            "index_version": "idx_a",
            "page_number": 2,
            "metadata": {"original_filename": "Intro.pdf"},
        }
    ]

    formatted = format_source_references(sources)

    assert "**Nguon tham khao:**" in formatted
    assert "Intro.pdf" in formatted
    assert "Trang 2" in formatted
    assert "chunk=123" in formatted
    assert "doc_version=docv_a" in formatted
    assert "index=idx_a" in formatted
