from unittest.mock import AsyncMock

import pytest

from core.checkpointing import (
    ThreadCheckpoint,
    build_graph_config,
    build_thread_id,
    open_postgres_checkpointer,
)


def test_thread_id_is_stable_per_user_and_session():
    first = build_thread_id(user_id="alice", session_id="s1")
    second = build_thread_id(user_id="alice", session_id="s1")

    assert first == second
    assert first.startswith("thread_")


def test_thread_id_changes_by_user_or_session():
    base = build_thread_id(user_id="alice", session_id="s1")

    assert base != build_thread_id(user_id="bob", session_id="s1")
    assert base != build_thread_id(user_id="alice", session_id="s2")


def test_checkpoint_serializes_resume_contract():
    checkpoint = ThreadCheckpoint(
        thread_id="thread_abc",
        state={"question": "What is AI?"},
        status="awaiting_approval",
        resume_token="resume_123",
    )

    assert checkpoint.to_record() == {
        "thread_id": "thread_abc",
        "state": {"question": "What is AI?"},
        "status": "awaiting_approval",
        "resume_token": "resume_123",
    }


def test_graph_config_contains_isolated_thread_id():
    config = build_graph_config(user_id="alice", session_id="session-1")

    assert config == {
        "recursion_limit": 15,
        "configurable": {"thread_id": build_thread_id("alice", "session-1")},
    }


@pytest.mark.asyncio
async def test_postgres_checkpointer_is_initialized_before_use():
    checkpointer = type("FakeCheckpointer", (), {"setup": AsyncMock()})()

    class FakeContext:
        async def __aenter__(self):
            return checkpointer

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    class FakeSaver:
        @classmethod
        def from_conn_string(cls, database_url):
            assert database_url == "postgresql://checkpoint-db"
            return FakeContext()

    async with open_postgres_checkpointer(
        "postgresql://checkpoint-db",
        saver_class=FakeSaver,
    ) as active_checkpointer:
        assert active_checkpointer is checkpointer
        checkpointer.setup.assert_awaited_once_with()
