import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.utils import get_mongo_connection, verify_token


logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )

    logger.info("Đang xác thực người dùng bằng token")
    token_data = verify_token(token)
    if token_data is None:
        logger.error("Xác thực token thất bại")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        collection = get_mongo_connection()
        username = token_data.get("username")
        if not username:
            raise credentials_exception

        user = collection.find_one({"_id": username})
        if not user:
            raise credentials_exception

        user_dict = dict(user)
        user_dict.pop("hashed_password", None)
        return user_dict
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Lỗi khi lấy dữ liệu người dùng: %s", exc)
        raise credentials_exception
