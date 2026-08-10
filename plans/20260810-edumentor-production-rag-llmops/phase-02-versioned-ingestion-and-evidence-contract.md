# Phase 02 - Versioned Ingestion And Evidence Contract

## Goal

Make all retrieved evidence stable, versioned, and safe to cite/cache.

## Files

- Create: `core/evidence.py`
- Create: `tests/test_evidence_contract.py`
- Create: `tests/test_document_indexer_contract.py`
- Modify: `indexing/document_indexer.py`
- Modify: `retrievers/ensemble_retriever.py`
- Modify: `core/learning_assistant_v2.py`

## Interfaces

- `build_document_id(course_id: str, filename: str, content_hash: str) -> str`
- `build_chunk_id(document_id: str, start_index: int, text: str) -> int`
- Retriever result metadata includes `document_id`, `chunk_id`, `document_version`, `index_version`, `source_file`, and `page_number` or `slide_number` when known.

## Steps

- [ ] Write failing unit tests for deterministic IDs and required evidence fields.
- [ ] Implement `core/evidence.py`.
- [ ] Update indexer metadata and primary IDs.
- [ ] Update retriever output normalization.
- [ ] Update source formatter to cite evidence IDs.
- [ ] Add idempotent re-index test with mocked collection.
- [ ] Commit phase.

## Acceptance Gate

- Re-indexing same content yields same IDs.
- A response cannot cite a source without document/chunk/version metadata.
- Cache and eval phases can consume the evidence contract.

