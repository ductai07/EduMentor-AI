# config.py (Kiểm tra lại và bổ sung nếu cần)
import os
from dotenv import load_dotenv

load_dotenv()

# --- Milvus Configuration ---
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
# Lấy collection name từ env, nếu không có thì dùng default
# Giá trị này có thể bị ghi đè bởi lifespan nếu cần
DEFAULT_COLLECTION_NAME = "learning_docs_v3"
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", DEFAULT_COLLECTION_NAME)

# --- Embedding Model ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- LLM Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))

# --- Web Search Configuration ---
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# --- Indexing Configuration ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# --- Upload Directory ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Logging ---
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()

# --- Retriever Configuration ---
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", 5))
VECTOR_WEIGHT = float(os.getenv("VECTOR_WEIGHT", 0.6))
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", 0.4))

# --- API Configuration ---
API_PORT = int(os.getenv("API_PORT", 5000))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 60)) # Timeout cho request /ask

# --- Simple Check ---
