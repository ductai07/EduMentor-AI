import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user
from api.schemas import ApiResponse
from auth.models import StatsResponse, StatsUpdate
from auth.utils import get_mongo_connection


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["legacy-stats"])


def ensure_owner_or_admin(current_user: dict, username: str, action: str):
    if current_user.get("username") != username and not current_user.get("is_admin", False):
        logger.warning(
            "Access denied: User %s attempted to %s stats of %s",
            current_user.get("username"),
            action,
            username,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không được phép thao tác thống kê của người dùng khác",
        )


@router.get("/{username}", response_model=StatsResponse)
async def get_user_stats(username: str, current_user: dict = Depends(get_current_user)):
    try:
        ensure_owner_or_admin(current_user, username, "read")
        collection = get_mongo_connection()
        user_data = collection.find_one({"_id": username})

        if not user_data:
            logger.warning("Không tìm thấy người dùng: %s", username)
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        stats_data = {
            "username": username,
            "last_activity": user_data.get("last_activity", None),
            "subjects": {},
            "documents": [],
            "flashcards": {},
            "completed_quizzes": len(user_data.get("completed_quizzes", [])),
            "chat_history_count": user_data.get("chat_history_count", 0),
            "recommendations": [],
        }

        if "stats" not in user_data or not isinstance(user_data["stats"], dict):
            user_data["stats"] = {}
            collection.update_one({"_id": username}, {"$set": {"stats": {}}})
            logger.info("Initialized empty stats for user: %s", username)

        if isinstance(user_data.get("documents"), list):
            stats_data["documents"] = user_data["documents"]
        if isinstance(user_data.get("flashcards"), dict):
            stats_data["flashcards"] = user_data["flashcards"]

        for subject, data in user_data["stats"].items():
            if not isinstance(data, dict):
                logger.warning("Invalid stats data format for subject %s: %s", subject, data)
                continue

            progress_updated_at = data.get("progress_updated_at")
            if progress_updated_at is not None and not isinstance(progress_updated_at, datetime):
                logger.warning("Invalid progress_updated_at format for %s: %s", subject, progress_updated_at)
                progress_updated_at = None

            stats_data["subjects"][subject] = {
                "progress": data.get("progress", 0),
                "progress_updated_at": progress_updated_at,
                "description": data.get("description", None),
            }

        incomplete_subjects = [
            subject for subject, data in stats_data["subjects"].items() if data["progress"] < 100
        ]
        if incomplete_subjects:
            stats_data["recommendations"].append(
                f"Tiếp tục học môn {incomplete_subjects[0]} để hoàn thành tiến độ."
            )

        if stats_data["last_activity"]:
            last_activity_time = stats_data["last_activity"]
            now = datetime.now(timezone.utc)
            if last_activity_time.tzinfo is None:
                last_activity_time = last_activity_time.replace(tzinfo=timezone.utc)

            days_since_last_activity = (now - last_activity_time).days
            if days_since_last_activity > 7:
                stats_data["recommendations"].append(
                    f"Bạn đã không hoạt động trong {days_since_last_activity} ngày. Hãy luyện tập đều đặn."
                )

        logger.info("Successfully retrieved stats for user: %s", username)
        return stats_data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi lấy thống kê người dùng: %s", exc)
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi lấy thống kê học tập")


@router.put("/update", response_model=ApiResponse)
async def update_user_stats(
    stats_update: StatsUpdate,
    current_user: dict = Depends(get_current_user),
):
    try:
        username = stats_update.username
        ensure_owner_or_admin(current_user, username, "update")

        collection = get_mongo_connection()
        user_data = collection.find_one({"_id": username})
        if not user_data:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        if "stats" not in user_data:
            collection.update_one({"_id": username}, {"$set": {"stats": {}}})
            logger.info("Initialized empty stats for user: %s", username)

        update_data = {"last_activity": datetime.now(timezone.utc)}

        if stats_update.subject:
            subject = stats_update.subject
            progress = stats_update.progress if stats_update.progress is not None else 0
            update_data[f"stats.{subject}"] = {
                "progress": progress,
                "progress_updated_at": datetime.now(timezone.utc),
            }
            logger.info("Updating stats for user %s, subject %s: %s%%", username, subject, progress)

        if stats_update.flashcards:
            for card_id, review_data in stats_update.flashcards.items():
                update_data[f"flashcards.{card_id}"] = {
                    "correct_count": review_data.get("correct", 0),
                    "review_count": review_data.get("reviewed", 0),
                    "last_review": datetime.now(timezone.utc),
                }

        if stats_update.completed_quiz:
            quiz_data = stats_update.completed_quiz
            collection.update_one(
                {"_id": username},
                {
                    "$push": {
                        "completed_quizzes": {
                            "quiz_id": quiz_data.get("quiz_id"),
                            "score": quiz_data.get("score"),
                            "completed_at": datetime.now(timezone.utc),
                        }
                    }
                },
            )

        result = collection.update_one({"_id": username}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không thể cập nhật thống kê người dùng")

        return ApiResponse(
            response={"success": True, "message": "Đã cập nhật thống kê học tập"},
            metadata={"updated_fields": list(update_data.keys())},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi cập nhật thống kê người dùng: %s", exc)
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi cập nhật thống kê học tập")
