from fastapi import APIRouter, Response, status

from api import state


router = APIRouter(tags=["health"])


@router.get("/", summary="API status")
async def root():
    return {"status": "EduMentor API is running", "version": "2.0.0"}


@router.get("/health", summary="Liveness probe")
async def health():
    return {"status": "ok", "service": "edumentor-api", "version": "2.0.0"}


@router.get("/ready", summary="Readiness probe")
async def ready(response: Response):
    dependencies = {
        "assistant": "ready" if state.assistant is not None else "missing",
        "document_indexer": "ready" if state.document_indexer is not None else "missing",
    }
    is_ready = all(value == "ready" for value in dependencies.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if is_ready else "not_ready",
        "service": "edumentor-api",
        "dependencies": dependencies,
    }
