from core.model_policy import select_model_route


def test_direct_or_intent_tasks_use_fast_route():
    route = select_model_route(task_type="intent", requires_grounding=False)

    assert route.name == "edumentor-fast"


def test_grounded_reasoning_uses_quality_route():
    route = select_model_route(task_type="answer", requires_grounding=True)

    assert route.name == "edumentor-quality"


def test_local_preference_uses_local_route():
    route = select_model_route(task_type="answer", requires_grounding=False, prefer_local=True)

    assert route.name == "edumentor-local"
