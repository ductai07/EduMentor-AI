import pytest

from core.citations import CitationVerificationError, verify_citations


def test_verify_citations_accepts_known_chunk_and_versions():
    sources = [
        {"chunk_id": 123, "document_version": "docv_a", "index_version": "idx_a"},
        {"chunk_id": 456, "document_version": "docv_b", "index_version": "idx_a"},
    ]

    verify_citations(
        cited_chunk_ids=[123],
        retrieved_sources=sources,
        expected_index_version="idx_a",
    )


def test_verify_citations_rejects_unknown_chunk():
    with pytest.raises(CitationVerificationError, match="Unknown citation chunk"):
        verify_citations(
            cited_chunk_ids=[999],
            retrieved_sources=[{"chunk_id": 123, "document_version": "docv_a", "index_version": "idx_a"}],
            expected_index_version="idx_a",
        )


def test_verify_citations_rejects_stale_index_version():
    with pytest.raises(CitationVerificationError, match="stale index"):
        verify_citations(
            cited_chunk_ids=[123],
            retrieved_sources=[{"chunk_id": 123, "document_version": "docv_a", "index_version": "idx_old"}],
            expected_index_version="idx_new",
        )
