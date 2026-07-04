import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user
from api.schemas import ChatHistoryResponse
from auth.utils import get_mongo_connection


logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.get("/chat_history/{username}", response_model=ChatHistoryResponse)
async def get_user_chat_history(
    username: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
):
    try:
        if current_user.get("username") != username and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không được phép xem lịch sử trò chuyện của người dùng khác",
            )

        collection = get_mongo_connection()
        user_data = collection.find_one({"_id": username}, {"chat_history": {"$slice": -limit}})
        if not user_data:
            user_exists = collection.count_documents({"_id": username}) > 0
            if not user_exists:
                raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
            return ChatHistoryResponse(username=username, history=[])

        return ChatHistoryResponse(username=username, history=user_data.get("chat_history", []))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi lấy lịch sử trò chuyện của %s: %s", username, exc)
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi lấy lịch sử trò chuyện")
