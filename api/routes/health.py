from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/", summary="Kiểm tra trạng thái API")
async def root():
    return {"status": "EduMentor API is running", "version": "2.0.0"}
