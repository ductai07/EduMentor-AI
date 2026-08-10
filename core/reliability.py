import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 2,
    backoff_seconds: float = 0.05,
    retry_exceptions: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError),
) -> T:
    last_error: BaseException | None = None
    for attempt in range(max(1, attempts)):
        try:
            return await operation()
        except retry_exceptions as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            await asyncio.sleep(backoff_seconds * (attempt + 1))
    if last_error:
        raise last_error
    raise RuntimeError("retry_async received no attempts")


def has_confident_source(sources: list[dict], min_score: float) -> bool:
    return any(float(source.get("score", 0.0) or 0.0) >= min_score for source in sources)


def filter_sources_by_score(sources: list[dict], min_score: float) -> list[dict]:
    return [
        source
        for source in sources
        if float(source.get("score", 0.0) or 0.0) >= min_score
    ]
