from datetime import datetime
import json
from .base_tool import BaseTool

class FlashcardGeneratorTool(BaseTool):
    @property
    def name(self) -> str:
        return "Flashcard_Generator"
    
    @property
    def description(self) -> str:
        return "Tạo flashcards cho một chủ đề."
    
    async def execute(self, assistant, **kwargs):
        topic = kwargs.get("question", "")
        if not topic.strip():
            return "Vui lòng cung cấp chủ đề để tạo flashcard."
        
        try:
            context = await assistant.retriever.search(topic)
            if not context:
                return f"Không tìm thấy thông tin về '{topic}' để tạo flashcard."
            
            context_text = "\n\n".join([f"Slide {doc.get('slide_number', 'N/A')}: {doc['text']}" for doc in context])
            prompt = f"""Dựa trên thông tin sau, tạo bộ flashcard học tập cho chủ đề "{topic}".
            Thông tin: {context_text}
            
            Tạo 10 flashcard, mỗi flashcard có định dạng:
            FLASHCARD #[số]:
            Mặt trước: [Câu hỏi hoặc thuật ngữ]
            Mặt sau: [Câu trả lời hoặc định nghĩa, kèm số slide nếu có]
            
            Flashcard nên bao gồm các khái niệm quan trọng, định nghĩa, công thức, và ứng dụng liên quan đến chủ đề. Sắp xếp theo thứ tự slide nếu có."""
            
            response = assistant.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Lưu flashcards vào lịch sử (có thể mở rộng để lưu vào cơ sở dữ liệu)
            try:
                self._save_flashcards_history(topic, content)
            except:
                # Không làm gián đoạn luồng chính nếu lưu lịch sử thất bại
                pass
                
            return content
        except Exception as e:
            return f"Lỗi khi tạo flashcard cho '{topic}': {str(e)}"
    
    def _save_flashcards_history(self, topic: str, content: str):
        """Lưu lịch sử flashcards đã tạo"""
        try:
            history_file = "flashcards_history.json"
            history = {}
            
            # Đọc lịch sử hiện có nếu có
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                history = {}
            
            # Thêm flashcards mới
            history[topic] = {
                "content": content,
                "created_at": datetime.now().isoformat()
            }
            
            # Lưu lại lịch sử
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception:
            # Bỏ qua lỗi khi lưu lịch sử
            pass