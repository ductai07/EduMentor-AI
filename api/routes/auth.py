import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import get_current_user
from auth.models import Token, UserBase, UserCreate, UserLogin, UserUpdate
from auth.utils import (
    authenticate_user,
    create_access_token,
    get_mongo_connection,
    get_password_hash,
)


logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


def build_token_response(user: dict):
    return {
        "access_token": create_access_token(data={"sub": user["username"]}),
        "token_type": "bearer",
        "username": user["username"],
        "full_name": user.get("full_name"),
    }


def update_last_login(username: str):
    try:
        collection = get_mongo_connection()
        collection.update_one(
            {"_id": username},
            {"$set": {"last_login": datetime.now(timezone.utc)}},
        )
    except Exception as exc:
        logger.error("Lỗi khi cập nhật lần đăng nhập cuối: %s", exc)


@router.post("/register", response_model=Token)
async def register_user(user: UserCreate):
    try:
        collection = get_mongo_connection()
        existing_user = collection.find_one({"_id": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username đã tồn tại")

        now_utc = datetime.now(timezone.utc)
        user_data = {
            "_id": user.username,
            "username": user.username,
            "hashed_password": get_password_hash(user.password),
            "email": user.email,
            "full_name": user.full_name,
            "created_at": now_utc,
            "updated_at": now_utc,
        }
        collection.insert_one(user_data)
        logger.info("Người dùng mới đã đăng ký: %s", user.username)

        return build_token_response(user_data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi đăng ký người dùng: %s", exc)
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi đăng ký người dùng")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    update_last_login(user["username"])
    return build_token_response(user)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
        )

    update_last_login(user["username"])
    return build_token_response(user)


@router.get("/me", response_model=UserBase)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    try:
        if not current_user or "username" not in current_user:
            logger.error("Dữ liệu người dùng trong token không hợp lệ: %s", current_user)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Thông tin người dùng không hợp lệ",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "username": current_user["username"],
            "email": current_user.get("email"),
            "full_name": current_user.get("full_name"),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi lấy hồ sơ người dùng: %s", exc)
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi lấy thông tin người dùng")


@router.put("/me", response_model=UserBase)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    try:
        username = current_user.get("username")
        collection = get_mongo_connection()

        update_data = {"updated_at": datetime.now(timezone.utc)}
        if user_update.email is not None:
            update_data["email"] = user_update.email
        if user_update.full_name is not None:
            update_data["full_name"] = user_update.full_name
        if user_update.password is not None:
            update_data["hashed_password"] = get_password_hash(user_update.password)

        result = collection.update_one({"_id": username}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        updated_user = collection.find_one({"_id": username})
        return {
            "username": updated_user["username"],
            "email": updated_user.get("email"),
            "full_name": updated_user.get("full_name"),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi cập nhật hồ sơ người dùng: %s", exc)
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi cập nhật thông tin người dùng")
