from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path
import asyncio
import logging
from contextlib import asynccontextmanager
from core.learning_assistant_v2 import LearningAssistant
from indexing.document_indexer import DocumentIndexer

# Thiết lập logging thay vì print
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Biến toàn cục để lưu trữ tài nguyên
assistant = None
document_indexer = None

# Context manager để quản lý lifecycle của ứng dụng
@asynccontextmanager
async def lifespan(app: FastAPI):
    global assistant, document_indexer
    collection_name = os.getenv("MILVUS_COLLECTION_NAME", "learning_docs_default")
    logger.info(f"Starting EduMentor API with Milvus collection: {collection_name}")

    try:
        assistant = LearningAssistant(collection_name=collection_name)
        document_indexer = DocumentIndexer(collection_name=collection_name)
        logger.info("LearningAssistant and DocumentIndexer initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Error initializing resources: {e}")
        raise
    finally:
        logger.info("Shutting down EduMentor API")
        if assistant:
            try:
                assistant.close()
                logger.info("LearningAssistant closed")
            except Exception as e:
                logger.error(f"Error closing LearningAssistant: {e}")
        if document_indexer and hasattr(document_indexer, 'close'):
            try:
                document_indexer.close()
                logger.info("DocumentIndexer closed")
            except Exception as e:
                logger.error(f"Error closing DocumentIndexer: {e}")

# Khởi tạo FastAPI app
app = FastAPI(
    title="EduMentor API",
    description="API cho hệ thống hỗ trợ học tập EduMentor",
    version="2.0.0",
    lifespan=lifespan
)

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cập nhật danh sách này trong production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Định nghĩa các model Pydantic
class ToolRequest(BaseModel):
    action: str
    input: str
    context: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class AskRequest(BaseModel):
    question: str

class UploadResponse(BaseModel):
    success: bool
    filename: str
    indexed: bool
    documents_added: int
    file_type: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    response: Any
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

# Thư mục lưu trữ file upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- Endpoints API ---

@app.post("/upload", response_model=UploadResponse)
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload file và chạy indexing trong background."""
    try:
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.pptx', '.ppt'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
            )

        # Tạo tên file duy nhất để tránh xung đột
        safe_filename = f"{Path(file.filename).stem}_{os.urandom(4).hex()}{file_ext}"
        file_location = UPLOAD_DIR / safe_filename

        # Lưu file
        try:
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
        except IOError as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Không thể lưu file: {e}")

        # Hàm chạy indexing trong background
        def run_indexing(location: Path, ext: str):
            logger.info(f"Indexing file {location.name} in background")
            try:
                metadata = {"original_filename": file.filename}
                if ext == '.pdf':
                    result = document_indexer.index_pdf(str(location), metadata=metadata)
                elif ext in ['.pptx', '.ppt']:
                    result = document_indexer.index_document(str(location), file_type="pptx", doc_metadata=metadata)
                elif ext in ['.docx', '.doc']:
                    result = document_indexer.index_document(str(location), file_type="docx", doc_metadata=metadata)
                else:  # .txt
                    result = document_indexer.index_document(str(location), doc_metadata=metadata)
                
                if result.get("success"):
                    logger.info(f"Indexed {location.name}: {result.get('documents_added', 0)} chunks added")
                else:
                    logger.error(f"Indexing failed for {location.name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"Error indexing {location.name}: {e}")

        background_tasks.add_task(run_indexing, file_location, file_ext)

        return UploadResponse(
            success=True,
            filename=file.filename,
            indexed=False,  # Indexing chưa hoàn thành
            documents_added=0,
            file_type=file_ext,
            message="File đã được nhận và đang được xử lý trong background",
            metadata={"saved_as": safe_filename}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /upload: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ: {str(e)}")

@app.post("/ask", response_model=ApiResponse)
async def ask_question(request: AskRequest):
    """Xử lý câu hỏi từ người dùng."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    if not assistant:
        raise HTTPException(status_code=503, detail="Hệ thống đang khởi động, vui lòng thử lại sau")

    try:
        logger.info(f"Processing question: {request.question[:100]}...")
        result = await asyncio.wait_for(assistant.answer(request.question), timeout=60.0)

        if not result or "response" not in result:
            logger.error(f"Invalid response from workflow: {result}")
            raise HTTPException(status_code=500, detail="Không thể tạo câu trả lời từ workflow")

        metadata = {
            "timestamp": asyncio.get_event_loop().time(),
            "route_decision": result.get("metadata", {}).get("route_decision"),
            "selected_tool": result.get("metadata", {}).get("selected_tool"),
            "executed_tools": list(result.get("tool_outputs", {}).keys()) if result.get("tool_outputs") else []
        }

        return ApiResponse(
            response=result["response"],
            sources=result.get("sources", []),
            metadata=metadata
        )
    except asyncio.TimeoutError:
        logger.warning(f"Timeout processing question: {request.question[:50]}...")
        return ApiResponse(
            response="Quá thời gian xử lý câu hỏi. Vui lòng thử lại.",
            sources=[],
            metadata={"error": "timeout"}
        )
    except Exception as e:
        logger.error(f"Error processing /ask: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ khi xử lý câu hỏi: {str(e)}")

@app.post("/tools", response_model=ApiResponse)
async def use_tool(request: ToolRequest):
    """Thực thi công cụ cụ thể."""
    tool_map = {
        "quiz": "Quiz_Generator",
        "flashcards": "Flashcard_Generator",
        "study_plan": "Study_Plan_Creator",
        "concept": "Concept_Explainer",
        "summary": "Summary_Generator",
        "mindmap": "Mind_Map_Creator",
        "progress": "Progress_Tracker",
        "rag": "RAG_Search"
    }

    tool_name = tool_map.get(request.action.lower())
    if not tool_name:
        raise HTTPException(status_code=400, detail=f"Hành động '{request.action}' không được hỗ trợ")

    if not assistant or not assistant.tool_registry.has_tool(tool_name):
        raise HTTPException(status_code=404, detail=f"Công cụ '{tool_name}' không tồn tại")

    try:
        tool_kwargs = {"question": request.input}
        if request.context:
            tool_kwargs["context"] = request.context
        if request.options:
            tool_kwargs.update(request.options)

        logger.info(f"Executing tool: {tool_name} with input: {request.input[:50]}...")
        result = await assistant.tool_registry.execute_tool(tool_name, **tool_kwargs)

        return ApiResponse(
            response=result,
            metadata={"tool_executed": tool_name, "input_provided": request.input[:100]}
        )
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi chạy công cụ '{tool_name}': {str(e)}")

@app.get("/", summary="Kiểm tra trạng thái API")
async def root():
    """Kiểm tra trạng thái API."""
    return {"status": "EduMentor API is running", "version": "2.0.0"}

