import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api import state
from api.dependencies import get_current_user
from api.schemas import ApiResponse, AskRequest
from config.settings import API_TIMEOUT


logger = logging.getLogger(__name__)
router = APIRouter(tags=["learning"])


@router.post("/ask", response_model=ApiResponse)
async def ask_question(
    request: AskRequest,
    current_user: Optional[dict] = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    if not state.assistant:
        raise HTTPException(
            status_code=503,
            detail="Hệ thống đang khởi động, vui lòng thử lại sau",
        )

    try:
        username = current_user.get("username") if current_user else None
        logger.info(
            "Processing question for user '%s': %s...",
            username or "anonymous",
            request.question[:100],
        )
        result = await asyncio.wait_for(
            state.assistant.answer(
                request.question,
                username=username,
                session_id=request.session_id,
            ),
            timeout=API_TIMEOUT,
        )

        if not result or "response" not in result:
            logger.error("Invalid response from workflow: %s", result)
            raise HTTPException(
                status_code=500,
                detail="Không thể tạo câu trả lời từ workflow",
            )

        metadata = {
            "timestamp": asyncio.get_event_loop().time(),
            "route_decision": result.get("metadata", {}).get("route_decision"),
            "selected_tool": result.get("metadata", {}).get("selected_tool"),
            "thread_id": result.get("metadata", {}).get("thread_id"),
            "executed_tools": list(result.get("tool_outputs", {}).keys())
            if result.get("tool_outputs")
            else [],
        }
        return ApiResponse(
            response=result["response"],
            sources=result.get("sources", []),
            metadata=metadata,
        )
    except asyncio.TimeoutError:
        logger.warning("Timeout processing question: %s...", request.question[:50])
        return ApiResponse(
            response="Quá thời gian xử lý câu hỏi. Vui lòng thử lại.",
            sources=[],
            metadata={"error": "timeout"},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error processing /ask: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi máy chủ khi xử lý câu hỏi: {exc}",
        )
