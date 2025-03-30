# --- START OF FILE tools/quiz_generator.py ---

import asyncio
from .base_tool import BaseTool
from typing import TYPE_CHECKING, Any # Thêm Any nếu cần cho type hint khác

# --- Khối TYPE_CHECKING duy nhất và đúng ---
# Khối này chỉ được xử lý bởi trình kiểm tra kiểu, không chạy lúc runtime
# Nó ngăn lỗi circular import khi gợi ý kiểu cho LearningAssistant
if TYPE_CHECKING:
    from core.learning_assistant_v2 import LearningAssistant
# --- Kết thúc khối TYPE_CHECKING ---

import logging

# Thiết lập logger cho module này
# Nên đặt logger sau các import
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Sử dụng __name__ cho logger

class QuizGenerator(BaseTool):
    @property
    def name(self) -> str:
        return "Quiz_Generator"

    @property
    def description(self) -> str:
        # Giữ mô tả tiếng Việt như yêu cầu trước đó
        return "Tạo câu hỏi trắc nghiệm (quiz) về một chủ đề cụ thể dựa trên tài liệu đã cung cấp."

    # needs_context mặc định là True trong BaseTool, phù hợp với QuizGenerator

    async def execute(self, assistant: 'LearningAssistant', **kwargs) -> str: # Thêm gợi ý kiểu trả về -> str
        """
        Thực thi việc tạo quiz một cách bất đồng bộ.
        """
        topic = kwargs.get("question", "") # Giả định 'question' chứa chủ đề cho quiz
        context_str = kwargs.get("context", "") # Lấy ngữ cảnh nếu được cung cấp bởi graph

        if not topic:
            logger.warning("QuizGenerator: Chủ đề không được cung cấp.")
            return "Vui lòng cung cấp chủ đề cho bài kiểm tra."

        # Sử dụng ngữ cảnh nếu có, nếu không thì truy xuất (mặc dù graph nên xử lý việc này)
        # Khối này chủ yếu để phòng ngừa hoặc cho test độc lập tool
        if not context_str and self.needs_context:
             logger.warning(f"QuizGenerator: Ngữ cảnh không được cung cấp cho chủ đề '{topic}', đang thử truy xuất.")
             try:
                 # Gọi hàm search async của retriever
                 retrieved_docs = await assistant.retriever.search(topic)
                 if not retrieved_docs:
                      logger.warning(f"QuizGenerator: Không tìm thấy tài liệu cho '{topic}'.")
                      return f"Không tìm thấy thông tin về '{topic}' để tạo bài kiểm tra."
                 # Format ngữ cảnh từ kết quả truy xuất
                 context_str = "\n\n".join([f"Slide {doc.get('slide_number', 'N/A')}: {doc.get('text', '')}" for doc in retrieved_docs])
             except Exception as e:
                  logger.error(f"QuizGenerator: Lỗi truy xuất ngữ cảnh: {e}")
                  return f"Lỗi khi truy xuất thông tin cho '{topic}': {e}"
        elif not context_str and not self.needs_context:
             # Trường hợp tool không cần context nhưng context lại rỗng
             context_str = "Không có ngữ cảnh được cung cấp hoặc yêu cầu."
        elif not context_str: # Trường hợp không mong muốn: cần context nhưng không có sau khi thử truy xuất
             logger.error(f"QuizGenerator: Thiếu ngữ cảnh cho '{topic}' mặc dù cần thiết.")
             return f"Lỗi: Thiếu ngữ cảnh cần thiết để tạo quiz cho '{topic}'."

        # Giữ prompt tiếng Việt
        prompt_template = f"""Dựa trên thông tin ngữ cảnh sau đây về chủ đề "{topic}", hãy tạo một bài kiểm tra trắc nghiệm.

        Ngữ cảnh:
        {context_str}

        Yêu cầu:
        - Tạo 5 câu hỏi trắc nghiệm.
        - Mỗi câu hỏi phải có 4 lựa chọn (A, B, C, D).
        - Chỉ có một đáp án đúng cho mỗi câu.
        - Đánh dấu rõ ràng đáp án đúng (ví dụ: bằng dấu * hoặc ghi chú riêng).
        - Câu hỏi nên bao quát các khía cạnh quan trọng của chủ đề trong ngữ cảnh.

        Định dạng output mong muốn:
        Câu 1: [Nội dung câu hỏi]
        A. [Lựa chọn A]
        B. [Lựa chọn B]
        C. [Lựa chọn C]
        D. [Lựa chọn D]
        Đáp án đúng: [A/B/C/D]

        Câu 2: ... (tương tự)
        ...
        """
        try:
            logger.info(f"QuizGenerator: Gọi LLM để tạo quiz cho '{topic}'...")
            # Sử dụng ainvoke cho gọi LLM bất đồng bộ
            response = await assistant.llm.ainvoke(prompt_template)
            # Truy cập nội dung trả về (có thể cần điều chỉnh tùy theo thư viện LLM)
            content = response # GoogleGenerativeAI có thể trả về trực tiếp nội dung
            # content = response.content if hasattr(response, 'content') else str(response) # Cách khác nếu là object
            logger.info(f"QuizGenerator: Đã tạo quiz cho '{topic}'.")
            return content
        except Exception as e:
            logger.exception(f"QuizGenerator: Lỗi khi gọi LLM: {e}")
            return f"Đã xảy ra lỗi khi tạo bài kiểm tra cho '{topic}': {str(e)}"

# --- END OF FILE tools/quiz_generator.py ---