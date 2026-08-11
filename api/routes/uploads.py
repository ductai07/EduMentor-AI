import logging
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from api import state
from api.schemas import UploadResponse
from config.settings import MAX_UPLOAD_BYTES, UPLOAD_DIR as UPLOAD_DIR_NAME


logger = logging.getLogger(__name__)
router = APIRouter(tags=["uploads"])

UPLOAD_DIR = Path(UPLOAD_DIR_NAME)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt"}
UPLOAD_CHUNK_BYTES = 1024 * 1024
OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def validate_file_signature(extension: str, content: bytes) -> None:
    valid = False
    if extension == ".pdf":
        valid = content.startswith(b"%PDF-")
    elif extension in {".docx", ".pptx"}:
        valid = content.startswith(b"PK\x03\x04")
    elif extension in {".doc", ".ppt"}:
        valid = content.startswith(OLE_SIGNATURE)
    elif extension == ".txt":
        try:
            content.decode("utf-8")
            valid = b"\x00" not in content
        except UnicodeDecodeError:
            valid = False

    if not valid:
        raise HTTPException(
            status_code=400,
            detail="File content does not match the declared file type.",
        )


async def save_upload(
    upload: UploadFile,
    destination: Path,
    extension: str,
    max_bytes: int,
) -> int:
    total_bytes = 0
    output: BinaryIO | None = None
    try:
        first_chunk = await upload.read(UPLOAD_CHUNK_BYTES)
        validate_file_signature(extension, first_chunk)
        output = open(destination, "xb")

        chunk = first_chunk
        while chunk:
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds the {max_bytes}-byte upload limit.",
                )
            await run_in_threadpool(output.write, chunk)
            chunk = await upload.read(UPLOAD_CHUNK_BYTES)
        return total_bytes
    except Exception:
        if output:
            output.close()
        destination.unlink(missing_ok=True)
        raise
    finally:
        if output and not output.closed:
            output.close()


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
        if not file.filename:
            raise HTTPException(status_code=400, detail="A filename is required.")
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        safe_filename = f"{uuid4().hex}{file_ext}"
        file_location = UPLOAD_DIR / safe_filename

        try:
            saved_bytes = await save_upload(
                file,
                file_location,
                file_ext,
                max_bytes=MAX_UPLOAD_BYTES,
            )
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
            metadata={"saved_as": safe_filename, "size_bytes": saved_bytes},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in /upload: %s", exc)
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ: {exc}")
