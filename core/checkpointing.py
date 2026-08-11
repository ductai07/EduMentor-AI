import hashlib
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator


def build_thread_id(user_id: str, session_id: str) -> str:
    digest = hashlib.sha256(f"{user_id}:{session_id}".encode("utf-8")).hexdigest()[:16]
    return f"thread_{digest}"


def build_graph_config(user_id: str, session_id: str) -> dict[str, Any]:
    return {
        "recursion_limit": 15,
        "configurable": {"thread_id": build_thread_id(user_id, session_id)},
    }


@asynccontextmanager
async def open_postgres_checkpointer(
    database_url: str,
    saver_class: Any | None = None,
) -> AsyncIterator[Any]:
    if saver_class is None:
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Install langgraph-checkpoint-postgres to enable durable checkpoints."
            ) from exc
        saver_class = AsyncPostgresSaver

    async with saver_class.from_conn_string(database_url) as checkpointer:
        await checkpointer.setup()
        yield checkpointer


@dataclass(frozen=True)
class ThreadCheckpoint:
    thread_id: str
    state: dict[str, Any]
    status: str
    resume_token: str | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "state": self.state,
            "status": self.status,
            "resume_token": self.resume_token,
        }
