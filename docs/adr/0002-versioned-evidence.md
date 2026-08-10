# ADR 0002 - Version Evidence Before Cache And Eval

## Status

Accepted.

## Decision

Every retrieved chunk must carry stable evidence metadata: `document_id`, `chunk_id`, `document_version`, and `index_version`.

## Rationale

- Citation verification needs stable chunk IDs.
- Cache invalidation needs index version.
- Eval datasets need gold evidence IDs.

## Consequences

- Re-indexing must be idempotent.
- Metadata is part of the retrieval contract, not display-only data.
