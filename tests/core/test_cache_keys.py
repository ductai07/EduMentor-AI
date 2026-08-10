from core.cache import build_cache_key, normalize_query


def test_normalize_query_collapses_spacing_and_case():
    assert normalize_query("  What   Is AI? ") == "what is ai?"


def test_cache_key_is_stable_for_same_inputs():
    first = build_cache_key(
        namespace="retrieval",
        environment="production",
        course_id="ai101",
        user_scope="user-a",
        query="What is AI?",
        index_version="idx_a",
        embedding_model="all-MiniLM-L6-v2",
        retriever_config="hybrid-0.7-0.3-k5",
        model_route="edumentor-quality",
        prompt_version="prompt_v1",
        policy_version="policy_v1",
    )
    second = build_cache_key(
        namespace="retrieval",
        environment="production",
        course_id="ai101",
        user_scope="user-a",
        query="  what is ai? ",
        index_version="idx_a",
        embedding_model="all-MiniLM-L6-v2",
        retriever_config="hybrid-0.7-0.3-k5",
        model_route="edumentor-quality",
        prompt_version="prompt_v1",
        policy_version="policy_v1",
    )

    assert first == second


def test_cache_key_changes_by_course_user_and_index_version():
    base = {
        "namespace": "retrieval",
        "environment": "production",
        "course_id": "ai101",
        "user_scope": "user-a",
        "query": "What is AI?",
        "index_version": "idx_a",
        "embedding_model": "all-MiniLM-L6-v2",
        "retriever_config": "hybrid-0.7-0.3-k5",
        "model_route": "edumentor-quality",
        "prompt_version": "prompt_v1",
        "policy_version": "policy_v1",
    }

    key = build_cache_key(**base)

    assert key != build_cache_key(**{**base, "course_id": "logic"})
    assert key != build_cache_key(**{**base, "user_scope": "user-b"})
    assert key != build_cache_key(**{**base, "index_version": "idx_b"})
    assert key.startswith("edumentor:production:retrieval:")
