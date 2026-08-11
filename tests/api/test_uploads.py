from pathlib import Path

import pytest
from fastapi import HTTPException

from api.routes.uploads import save_upload, validate_file_signature


class ChunkedUpload:
    def __init__(self, chunks):
        self._chunks = iter(chunks)

    async def read(self, size):
        return next(self._chunks, b"")


@pytest.mark.parametrize(
    ("extension", "content"),
    [
        (".pdf", b"%PDF-1.7\n"),
        (".docx", b"PK\x03\x04document"),
        (".pptx", b"PK\x03\x04slides"),
        (".doc", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1document"),
        (".ppt", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1slides"),
        (".txt", b"plain UTF-8 text"),
    ],
)
def test_validate_file_signature_accepts_supported_content(extension, content):
    validate_file_signature(extension, content)


def test_validate_file_signature_rejects_extension_spoofing():
    with pytest.raises(HTTPException) as exc_info:
        validate_file_signature(".pdf", b"not a pdf")

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_save_upload_streams_chunks_to_disk(tmp_path: Path):
    destination = tmp_path / "document.pdf"
    upload = ChunkedUpload([b"%PDF-", b"content", b""])

    saved_bytes = await save_upload(upload, destination, ".pdf", max_bytes=32)

    assert saved_bytes == 12
    assert destination.read_bytes() == b"%PDF-content"


@pytest.mark.asyncio
async def test_save_upload_removes_partial_file_when_limit_is_exceeded(tmp_path: Path):
    destination = tmp_path / "document.pdf"
    upload = ChunkedUpload([b"%PDF-", b"too-large", b""])

    with pytest.raises(HTTPException) as exc_info:
        await save_upload(upload, destination, ".pdf", max_bytes=8)

    assert exc_info.value.status_code == 413
    assert not destination.exists()
