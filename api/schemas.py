from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ToolRequest(BaseModel):
    action: str
    input: str
    context: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class SpecificToolInput(BaseModel):
    input: str
    context: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class AskRequest(BaseModel):
    question: str


class QuizQuestion(BaseModel):
    id: int
    question_text: str
    options: List[str]
    correct_answer_index: int


class QuizSubmission(BaseModel):
    quiz_id: str
    questions: List[QuizQuestion]
    answers: Dict[int, int]


class QuizResult(BaseModel):
    quiz_id: str
    score: float
    total_questions: int
    correct_count: int
    results: Dict[int, bool]
    feedback: Optional[str] = None


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


class ChatHistoryResponse(BaseModel):
    username: str
    history: List[Dict[str, Any]]

