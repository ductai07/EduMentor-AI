from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRoute:
    name: str
    model: str
    timeout_seconds: float = 30.0
    fallback_model: str | None = None


def select_model_route(
    task_type: str,
    requires_grounding: bool,
    prefer_local: bool = False,
) -> ModelRoute:
    if prefer_local:
        return ModelRoute(name="edumentor-local", model="edumentor-local", fallback_model="edumentor-fast")
    if task_type in {"intent", "emotion", "tool_selection"} and not requires_grounding:
        return ModelRoute(name="edumentor-fast", model="edumentor-fast", fallback_model="edumentor-quality")
    if requires_grounding:
        return ModelRoute(name="edumentor-quality", model="edumentor-quality", fallback_model="edumentor-fast")
    return ModelRoute(name="edumentor-fast", model="edumentor-fast", fallback_model="edumentor-quality")
