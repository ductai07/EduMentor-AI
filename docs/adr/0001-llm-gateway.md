# ADR 0001 - Use LiteLLM As Model Gateway

## Status

Accepted for implementation.

## Decision

Use LiteLLM as the OpenAI-compatible boundary between EduMentor and model providers.

## Rationale

- Keeps LangGraph nodes provider-agnostic.
- Supports logical model names such as `edumentor-fast`, `edumentor-quality`, and `edumentor-local`.
- Allows fallback and usage tracking to be tested without changing graph logic.

## Consequences

- Runtime needs LiteLLM configuration and master key management.
- Direct `GoogleGenerativeAI` calls must be migrated behind `LLMClient`.
