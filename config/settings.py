import os
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import urlsplit

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> None:
        return None


load_dotenv()

DEFAULT_COLLECTION_NAME = "learning_docs_v3"
DEFAULT_JWT_SECRET = "your-secret-key-please-change-in-production"


def parse_csv_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _get_int(env: Mapping[str, str], key: str, default: int) -> int:
    return int(env.get(key, str(default)))


def _get_float(env: Mapping[str, str], key: str, default: float) -> float:
    return float(env.get(key, str(default)))


def _get_bool(env: Mapping[str, str], key: str, default: bool) -> bool:
    value = env.get(key)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    ENVIRONMENT: str = "development"

    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"
    DEFAULT_COLLECTION_NAME: str = DEFAULT_COLLECTION_NAME
    MILVUS_COLLECTION: str = DEFAULT_COLLECTION_NAME

    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB_NAME: str = "edumentor"
    MONGODB_COLLECTION: str = "edumentor"
    MONGODB_URI: str = "mongodb://localhost:27017"

    JWT_SECRET_KEY: str = DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    GOOGLE_API_KEY: str | None = None
    NVIDIA_API_KEY: str | None = None
    NVIDIA_API_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    LLM_MODEL_NAME: str | None = None
    LLM_CHAT_MODEL: str = "openai/gpt-oss-20b"
    LLM_TEMPERATURE: float = 0.05
    EMBEDDING_API_BASE_URL: str | None = None
    EMBEDDING_DIMENSIONS: int = 384
    LITELLM_BASE_URL: str = "http://localhost:4000/v1"
    LITELLM_MASTER_KEY: str = "sk-edumentor-dev"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHECKPOINT_DATABASE_URL: str = "postgresql://edumentor:edumentor@localhost:5432/edumentor"
    LANGFUSE_HOST: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None

    SERPER_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_BYTES: int = 25 * 1024 * 1024
    LOGGING_LEVEL: str = "INFO"

    RETRIEVER_TOP_K: int = 5
    VECTOR_WEIGHT: float = 0.7
    BM25_WEIGHT: float = 0.3

    ALLOWED_TOOLS: list[str] = field(default_factory=list)
    TOOL_TIMEOUT_SECONDS: float = 20.0
    TOOL_OUTPUT_MAX_CHARS: int = 12000
    RETRY_ATTEMPTS: int = 2
    RETRY_BACKOFF_SECONDS: float = 0.05
    RETRIEVAL_MIN_SCORE: float = 0.15

    API_PORT: int = 5000
    API_HOST: str = "0.0.0.0"
    API_RELOAD: bool = False
    API_TIMEOUT: int = 120

    CORS_ALLOW_ORIGINS: list[str] = field(default_factory=lambda: ["*"])


def get_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    source = env or os.environ
    mongodb_host = source.get("MONGODB_HOST", "localhost")
    mongodb_port = _get_int(source, "MONGODB_PORT", 27017)
    return AppSettings(
        ENVIRONMENT=source.get("ENVIRONMENT", "development").lower(),
        MILVUS_HOST=source.get("MILVUS_HOST", "localhost"),
        MILVUS_PORT=source.get("MILVUS_PORT", "19530"),
        MILVUS_COLLECTION=source.get("MILVUS_COLLECTION", DEFAULT_COLLECTION_NAME),
        MONGODB_HOST=mongodb_host,
        MONGODB_PORT=mongodb_port,
        MONGODB_DB_NAME=source.get("MONGODB_DB_NAME", "edumentor"),
        MONGODB_COLLECTION=source.get("MONGODB_COLLECTION", "edumentor"),
        MONGODB_URI=source.get("MONGODB_URI", f"mongodb://{mongodb_host}:{mongodb_port}"),
        JWT_SECRET_KEY=source.get("JWT_SECRET_KEY", DEFAULT_JWT_SECRET),
        JWT_ALGORITHM=source.get("JWT_ALGORITHM", "HS256"),
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=_get_int(source, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24),
        EMBEDDING_MODEL=source.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        GOOGLE_API_KEY=source.get("GOOGLE_API_KEY"),
        NVIDIA_API_KEY=source.get("NVIDIA_API_KEY"),
        NVIDIA_API_BASE_URL=source.get("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        LLM_MODEL_NAME=source.get("LLM_MODEL_NAME"),
        LLM_CHAT_MODEL=source.get("LLM_CHAT_MODEL", "openai/gpt-oss-20b"),
        LLM_TEMPERATURE=_get_float(source, "LLM_TEMPERATURE", 0.05),
        EMBEDDING_API_BASE_URL=source.get("EMBEDDING_API_BASE_URL"),
        EMBEDDING_DIMENSIONS=_get_int(source, "EMBEDDING_DIMENSIONS", 384),
        LITELLM_BASE_URL=source.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
        LITELLM_MASTER_KEY=source.get("LITELLM_MASTER_KEY", "sk-edumentor-dev"),
        REDIS_URL=source.get("REDIS_URL", "redis://localhost:6379/0"),
        CHECKPOINT_DATABASE_URL=source.get(
            "CHECKPOINT_DATABASE_URL",
            "postgresql://edumentor:edumentor@localhost:5432/edumentor",
        ),
        LANGFUSE_HOST=source.get("LANGFUSE_HOST"),
        LANGFUSE_PUBLIC_KEY=source.get("LANGFUSE_PUBLIC_KEY"),
        LANGFUSE_SECRET_KEY=source.get("LANGFUSE_SECRET_KEY"),
        SERPER_API_KEY=source.get("SERPER_API_KEY"),
        TAVILY_API_KEY=source.get("TAVILY_API_KEY"),
        CHUNK_SIZE=_get_int(source, "CHUNK_SIZE", 500),
        CHUNK_OVERLAP=_get_int(source, "CHUNK_OVERLAP", 50),
        UPLOAD_DIR=source.get("UPLOAD_DIR", "uploads"),
        MAX_UPLOAD_BYTES=_get_int(source, "MAX_UPLOAD_BYTES", 25 * 1024 * 1024),
        LOGGING_LEVEL=source.get("LOGGING_LEVEL", "INFO").upper(),
        RETRIEVER_TOP_K=_get_int(source, "RETRIEVER_TOP_K", 5),
        VECTOR_WEIGHT=_get_float(source, "VECTOR_WEIGHT", 0.7),
        BM25_WEIGHT=_get_float(source, "BM25_WEIGHT", 0.3),
        ALLOWED_TOOLS=parse_csv_list(source.get("ALLOWED_TOOLS")),
        TOOL_TIMEOUT_SECONDS=_get_float(source, "TOOL_TIMEOUT_SECONDS", 20.0),
        TOOL_OUTPUT_MAX_CHARS=_get_int(source, "TOOL_OUTPUT_MAX_CHARS", 12000),
        RETRY_ATTEMPTS=_get_int(source, "RETRY_ATTEMPTS", 2),
        RETRY_BACKOFF_SECONDS=_get_float(source, "RETRY_BACKOFF_SECONDS", 0.05),
        RETRIEVAL_MIN_SCORE=_get_float(source, "RETRIEVAL_MIN_SCORE", 0.15),
        API_PORT=_get_int(source, "API_PORT", 5000),
        API_HOST=source.get("API_HOST", "0.0.0.0"),
        API_RELOAD=_get_bool(source, "API_RELOAD", False),
        API_TIMEOUT=_get_int(source, "API_TIMEOUT", 120),
        CORS_ALLOW_ORIGINS=parse_csv_list(source.get("CORS_ALLOW_ORIGINS")) or ["*"],
    )


def validate_production_settings(settings: AppSettings) -> None:
    if settings.ENVIRONMENT not in {"production", "staging"}:
        return
    if settings.JWT_SECRET_KEY == DEFAULT_JWT_SECRET or len(settings.JWT_SECRET_KEY) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be set to a strong non-default value in production")
    if "*" in settings.CORS_ALLOW_ORIGINS:
        raise RuntimeError("CORS_ALLOW_ORIGINS must not contain '*' in production")
    if settings.API_RELOAD:
        raise RuntimeError("API_RELOAD must be disabled in production")
    checkpoint_password = urlsplit(settings.CHECKPOINT_DATABASE_URL).password
    if not checkpoint_password or checkpoint_password == "edumentor":
        raise RuntimeError(
            "CHECKPOINT_DATABASE_URL must use a non-default database password in production"
        )


SETTINGS = get_settings()

ENVIRONMENT = SETTINGS.ENVIRONMENT

MILVUS_HOST = SETTINGS.MILVUS_HOST
MILVUS_PORT = SETTINGS.MILVUS_PORT
MILVUS_COLLECTION = SETTINGS.MILVUS_COLLECTION

MONGODB_HOST = SETTINGS.MONGODB_HOST
MONGODB_PORT = SETTINGS.MONGODB_PORT
MONGODB_DB_NAME = SETTINGS.MONGODB_DB_NAME
MONGODB_COLLECTION = SETTINGS.MONGODB_COLLECTION
MONGODB_URI = SETTINGS.MONGODB_URI

JWT_SECRET_KEY = SETTINGS.JWT_SECRET_KEY
JWT_ALGORITHM = SETTINGS.JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = SETTINGS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

EMBEDDING_MODEL = SETTINGS.EMBEDDING_MODEL
GOOGLE_API_KEY = SETTINGS.GOOGLE_API_KEY
NVIDIA_API_KEY = SETTINGS.NVIDIA_API_KEY
NVIDIA_API_BASE_URL = SETTINGS.NVIDIA_API_BASE_URL
LLM_MODEL_NAME = SETTINGS.LLM_MODEL_NAME
LLM_CHAT_MODEL = SETTINGS.LLM_CHAT_MODEL
LLM_TEMPERATURE = SETTINGS.LLM_TEMPERATURE
EMBEDDING_API_BASE_URL = SETTINGS.EMBEDDING_API_BASE_URL
EMBEDDING_DIMENSIONS = SETTINGS.EMBEDDING_DIMENSIONS
LITELLM_BASE_URL = SETTINGS.LITELLM_BASE_URL
LITELLM_MASTER_KEY = SETTINGS.LITELLM_MASTER_KEY
REDIS_URL = SETTINGS.REDIS_URL
CHECKPOINT_DATABASE_URL = SETTINGS.CHECKPOINT_DATABASE_URL
LANGFUSE_HOST = SETTINGS.LANGFUSE_HOST
LANGFUSE_PUBLIC_KEY = SETTINGS.LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY = SETTINGS.LANGFUSE_SECRET_KEY

SERPER_API_KEY = SETTINGS.SERPER_API_KEY
TAVILY_API_KEY = SETTINGS.TAVILY_API_KEY

CHUNK_SIZE = SETTINGS.CHUNK_SIZE
CHUNK_OVERLAP = SETTINGS.CHUNK_OVERLAP

UPLOAD_DIR = SETTINGS.UPLOAD_DIR
MAX_UPLOAD_BYTES = SETTINGS.MAX_UPLOAD_BYTES
os.makedirs(UPLOAD_DIR, exist_ok=True)

LOGGING_LEVEL = SETTINGS.LOGGING_LEVEL

RETRIEVER_TOP_K = SETTINGS.RETRIEVER_TOP_K
VECTOR_WEIGHT = SETTINGS.VECTOR_WEIGHT
BM25_WEIGHT = SETTINGS.BM25_WEIGHT
ALLOWED_TOOLS = SETTINGS.ALLOWED_TOOLS
TOOL_TIMEOUT_SECONDS = SETTINGS.TOOL_TIMEOUT_SECONDS
TOOL_OUTPUT_MAX_CHARS = SETTINGS.TOOL_OUTPUT_MAX_CHARS
RETRY_ATTEMPTS = SETTINGS.RETRY_ATTEMPTS
RETRY_BACKOFF_SECONDS = SETTINGS.RETRY_BACKOFF_SECONDS
RETRIEVAL_MIN_SCORE = SETTINGS.RETRIEVAL_MIN_SCORE

API_PORT = SETTINGS.API_PORT
API_HOST = SETTINGS.API_HOST
API_RELOAD = SETTINGS.API_RELOAD
API_TIMEOUT = SETTINGS.API_TIMEOUT

CORS_ALLOW_ORIGINS = SETTINGS.CORS_ALLOW_ORIGINS
