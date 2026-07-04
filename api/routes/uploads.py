import logging
import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from api import state
from api.schemas import UploadResponse
from config.settings import UPLOAD_DIR as UPLOAD_DIR_NAME


logger = logging.getLogger(__name__)
router = APIRouter(tags=["uploads"])

UPLOAD_DIR = Path(UPLOAD_DIR_NAME)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt"}


def index_uploaded_file(location: Path, original_filename: str, ext: str):
    logger.info("Indexing file %s in background", location.name)
    try:
        metadata = {"original_filename": original_filename}
        if ext in [".pptx", ".ppt"]:
            result = state.document_indexer.index_document(
                str(location),
                file_type="pptx",
                doc_metadata=metadata,
            )
        elif ext in [".docx", ".doc"]:
            result = state.document_indexer.index_document(
                str(location),
                file_type="docx",
                doc_metadata=metadata,
            )
        else:
            result = state.document_indexer.index_document(
                str(location),
                doc_metadata=metadata,
            )

        if result.get("success"):
            logger.info(
                "Indexed %s: %s chunks added",
                location.name,
                result.get("documents_added", 0),
            )
        else:
            logger.error(
                "Indexing failed for %s: %s",
                location.name,
                result.get("error", "Unknown error"),
            )
    except Exception as exc:
        logger.error("Error indexing %s: %s", location.name, exc)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        safe_filename = f"{Path(file.filename).stem}_{os.urandom(4).hex()}{file_ext}"
        file_location = UPLOAD_DIR / safe_filename

        try:
            with open(file_location, "wb") as output_file:
                output_file.write(await file.read())
        except IOError as exc:
            logger.error("Failed to save file %s: %s", file.filename, exc)
            raise HTTPException(status_code=500, detail=f"Không thể lưu file: {exc}")

        background_tasks.add_task(
            index_uploaded_file,
            file_location,
            file.filename,
            file_ext,
        )

        return UploadResponse(
            success=True,
            filename=file.filename,
            indexed=False,
            documents_added=0,
            file_type=file_ext,
            message="File đã được nhận và đang được xử lý trong background",
            metadata={"saved_as": safe_filename},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in /upload: %s", exc)
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ: {exc}")
