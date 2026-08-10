from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


class Indexer(Protocol):
    index_version: str

    def index_document(self, file_path: str, doc_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class IngestionConfig:
    source_dir: Path
    manifest_path: Path
    collection_name: str
    run_id: str


def discover_documents(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        return []
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        return {"indexed_files": {}}
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)


def build_file_fingerprint(path: Path) -> str:
    stat = path.stat()
    return f"{path.name}:{stat.st_size}:{int(stat.st_mtime)}"


def should_index(path: Path, manifest: dict[str, Any], force: bool = False) -> bool:
    if force:
        return True
    previous = manifest.get("indexed_files", {}).get(str(path))
    return not previous or previous.get("fingerprint") != build_file_fingerprint(path)


def index_documents(
    config: IngestionConfig,
    indexer: Indexer,
    *,
    force: bool = False,
) -> dict[str, Any]:
    manifest = load_manifest(config.manifest_path)
    indexed_files = manifest.setdefault("indexed_files", {})
    documents = discover_documents(config.source_dir)
    results = []

    for document_path in documents:
        if not should_index(document_path, manifest, force=force):
            results.append({"file": str(document_path), "status": "skipped"})
            continue

        metadata = {
            "original_filename": document_path.name,
            "ingestion_run_id": config.run_id,
            "collection_name": config.collection_name,
        }
        result = indexer.index_document(str(document_path), doc_metadata=metadata)
        status = "indexed" if result.get("success") else "failed"
        record = {
            "file": str(document_path),
            "status": status,
            "documents_added": result.get("documents_added", 0),
            "error": result.get("error"),
        }
        results.append(record)

        if result.get("success"):
            indexed_files[str(document_path)] = {
                "fingerprint": build_file_fingerprint(document_path),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "documents_added": result.get("documents_added", 0),
                "index_version": indexer.index_version,
                "run_id": config.run_id,
            }

    summary = {
        "run_id": config.run_id,
        "collection_name": config.collection_name,
        "source_dir": str(config.source_dir),
        "total_files": len(documents),
        "indexed": sum(1 for item in results if item["status"] == "indexed"),
        "skipped": sum(1 for item in results if item["status"] == "skipped"),
        "failed": sum(1 for item in results if item["status"] == "failed"),
        "results": results,
    }
    manifest["last_run"] = summary
    write_manifest(config.manifest_path, manifest)
    return summary
