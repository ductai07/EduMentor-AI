import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api import state
from api.routes import auth, chat, health, learning, legacy_stats, quiz, tools, uploads
from api.stats import router as stats_router
from auth.utils import get_mongo_connection
from config import settings as config


logging.basicConfig(
    level=getattr(logging, config.LOGGING_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_collection = None
    runtime_dependencies = None
    milvus_collection_name = os.getenv("MILVUS_COLLECTION_NAME", config.MILVUS_COLLECTION)
    logger.info("Starting EduMentor API with Milvus collection: %s", milvus_collection_name)

    try:
        mongo_collection = get_mongo_connection()
        logger.info(
            "Successfully connected to MongoDB collection: %s/%s",
            config.MONGODB_DB_NAME,
            config.MONGODB_COLLECTION,
        )
    except Exception as exc:
        logger.error(
            "NGHIÊM TRỌNG: Không thể kết nối MongoDB khi khởi động: %s. Một số tính năng có thể bị tắt.",
            exc,
        )

    try:
        from core.learning_assistant_v2 import LearningAssistant
        from core.runtime import build_runtime_dependencies
        from indexing.document_indexer import DocumentIndexer

        runtime_dependencies = build_runtime_dependencies(
            config,
            collection_name=milvus_collection_name,
        )
        state.assistant = LearningAssistant(
            mongo_collection=mongo_collection,
            collection_name=milvus_collection_name,
            cache_backend=runtime_dependencies.cache_backend,
            span_recorder=runtime_dependencies.span_recorder,
            index_version=runtime_dependencies.index_version,
        )
        state.document_indexer = DocumentIndexer(
            collection_name=milvus_collection_name,
            model_name=config.EMBEDDING_MODEL,
            host=config.MILVUS_HOST,
            port=config.MILVUS_PORT,
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
        )
        logger.info("Khởi tạo LearningAssistant và DocumentIndexer thành công")
        yield
    except Exception as exc:
        logger.error("Lỗi khi khởi tạo tài nguyên lõi: %s", exc)
        raise
    finally:
        logger.info("Đang tắt EduMentor API")
        if state.assistant:
            try:
                state.assistant.close()
                logger.info("LearningAssistant closed")
            except Exception as exc:
                logger.error("Lỗi khi đóng LearningAssistant: %s", exc)

        if state.document_indexer and hasattr(state.document_indexer, "close"):
            try:
                state.document_indexer.close()
                logger.info("DocumentIndexer closed")
            except Exception as exc:
                logger.error("Lỗi khi đóng DocumentIndexer: %s", exc)
        if runtime_dependencies:
            try:
                await runtime_dependencies.close()
                logger.info("Runtime dependencies closed")
            except Exception as exc:
                logger.error("Error closing runtime dependencies: %s", exc)


def add_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def create_app(enable_lifespan: bool = True) -> FastAPI:
    config.validate_production_settings(config.SETTINGS)
    app = FastAPI(
        title="EduMentor API",
        description="API cho hệ thống hỗ trợ học tập EduMentor",
        version="2.0.0",
        lifespan=lifespan if enable_lifespan else None,
    )

    add_request_id_middleware(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(uploads.router)
    app.include_router(learning.router)
    app.include_router(quiz.router)
    app.include_router(tools.router)
    app.include_router(auth.router)
    app.include_router(stats_router)
    app.include_router(legacy_stats.router)
    app.include_router(chat.router)
    return app


app = create_app()
