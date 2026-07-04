import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from api import state
from api.dependencies import get_current_user
from api.schemas import ApiResponse, SpecificToolInput


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tools", tags=["tools"])

TOOL_MAP = {
    "quiz": "Quiz_Generator",
    "flashcard": "Flashcard_Generator",
    "study_plan": "Study_Plan_Creator",
    "concept": "Concept_Explainer",
    "summary": "Summary_Generator",
    "mindmap": "Mind_Map_Creator",
    "progress": "Progress_Tracker",
    "rag": "RAG_Search",
    "web_search": "Web_Search",
}


@router.post("/{tool_name}", response_model=ApiResponse)
async def use_specific_tool(
    tool_name: str,
    request: SpecificToolInput,
    current_user: Dict = Depends(get_current_user),
):
    if tool_name not in TOOL_MAP:
        raise HTTPException(status_code=400, detail=f"Công cụ '{tool_name}' không được hỗ trợ")

    actual_tool_name = TOOL_MAP[tool_name]
    if not state.assistant or not state.assistant.tool_registry.has_tool(actual_tool_name):
        raise HTTPException(
            status_code=503,
            detail=f"Hệ thống đang khởi động hoặc công cụ '{actual_tool_name}' không khả dụng.",
        )

    try:
        tool_kwargs = {"question": request.input}
        if request.context:
            tool_kwargs["context"] = request.context

        options = request.options or {}
        if not options.get("username") and current_user.get("username"):
            options["username"] = current_user.get("username")
            logger.info(
                "Setting authenticated username '%s' for tool %s",
                options["username"],
                actual_tool_name,
            )

        if options:
            tool_kwargs["options"] = options

        logger.info("Executing tool: %s with input: %s...", actual_tool_name, request.input[:50])
        result = await state.assistant.tool_registry.execute_tool(actual_tool_name, **tool_kwargs)
        return ApiResponse(
            response=result,
            metadata={"tool_executed": actual_tool_name, "input_provided": request.input[:100]},
        )
    except Exception as exc:
        logger.error("Error executing tool %s: %s", actual_tool_name, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi chạy công cụ '{actual_tool_name}': {exc}",
        )
