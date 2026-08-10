from core.checkpointing import ThreadCheckpoint, build_thread_id


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
