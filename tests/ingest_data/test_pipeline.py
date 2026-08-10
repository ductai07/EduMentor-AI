from pathlib import Path

from ingest_data.pipeline import IngestionConfig, discover_documents, index_documents


class FakeIndexer:
    index_version = "idx-test"

    def __init__(self) -> None:
        self.calls = []

    def index_document(self, file_path, doc_metadata=None):
        self.calls.append({"file_path": file_path, "metadata": doc_metadata})
        return {"success": True, "documents_added": 2}


def test_discover_documents_filters_supported_files(tmp_path: Path):
    (tmp_path / "lesson.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "ignore.png").write_text("no", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "notes.docx").write_text("doc", encoding="utf-8")

    assert [path.name for path in discover_documents(tmp_path)] == ["lesson.txt", "notes.docx"]


def test_index_documents_writes_manifest_and_skips_unchanged_files(tmp_path: Path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "lesson.txt").write_text("logic", encoding="utf-8")
    manifest_path = tmp_path / "reports" / "manifest.json"
    config = IngestionConfig(
        source_dir=source_dir,
        manifest_path=manifest_path,
        collection_name="learning_docs",
        run_id="run-1",
    )
    indexer = FakeIndexer()

    first = index_documents(config, indexer)
    second = index_documents(config, indexer)

    assert first["indexed"] == 1
    assert second["skipped"] == 1
    assert len(indexer.calls) == 1
    assert manifest_path.exists()
