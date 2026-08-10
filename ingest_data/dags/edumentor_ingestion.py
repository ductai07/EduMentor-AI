from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task


PROJECT_ROOT = Path(os.getenv("EDUMENTOR_PROJECT_ROOT", "/opt/edumentor"))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_ARGS = {
    "owner": "edumentor",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="edumentor_ingest_documents",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 8, 10),
    schedule=None,
    catchup=False,
    tags=["edumentor", "rag", "ingestion"],
)
def edumentor_ingest_documents():
    @task()
    def run_ingestion() -> dict:
        from config import settings as config
        from indexing.document_indexer import DocumentIndexer
        from ingest_data.pipeline import IngestionConfig, index_documents

        run_id = os.getenv("AIRFLOW_CTX_DAG_RUN_ID", datetime.utcnow().isoformat())
        source_dir = Path(os.getenv("INGEST_SOURCE_DIR", "/opt/airflow/source_documents"))
        manifest_path = Path(os.getenv("INGEST_MANIFEST_PATH", "/opt/airflow/reports/manifest.json"))
        collection_name = os.getenv("MILVUS_COLLECTION", config.MILVUS_COLLECTION)

        indexer = DocumentIndexer(
            collection_name=collection_name,
            model_name=config.EMBEDDING_MODEL,
            host=os.getenv("MILVUS_HOST", config.MILVUS_HOST),
            port=os.getenv("MILVUS_PORT", config.MILVUS_PORT),
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
        )
        try:
            return index_documents(
                IngestionConfig(
                    source_dir=source_dir,
                    manifest_path=manifest_path,
                    collection_name=collection_name,
                    run_id=run_id,
                ),
                indexer,
                force=os.getenv("INGEST_FORCE", "false").lower() in {"1", "true", "yes"},
            )
        finally:
            indexer.close()

    run_ingestion()


edumentor_ingest_documents()
