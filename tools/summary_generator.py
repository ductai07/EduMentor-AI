from datetime import datetime
from .base_tool import BaseTool

class SummaryGeneratorTool(BaseTool):
    @property
    def name(self) -> str:
        return "Summary_Generator"
    
    @property
    def description(self) -> str:
        return "Tạo tóm tắt cho một chủ đề."
    
    async def execute(self, assistant, **kwargs):
        topic = kwargs.get("question", "")
        if not topic.strip():
            return "Vui lòng cung cấp chủ đề để tạo tóm tắt."
        
        try:
            context = await  assistant.retriever.search(topic)
            if not context:
                return f"Không tìm thấy thông tin về '{topic}' để tạo tóm tắt."
            
            context_text = "\n\n".join([doc["text"] for doc in context])
            prompt = f"""Dựa trên thông tin sau, tạo bản tóm tắt ngắn gọn và dễ hiểu về chủ đề "{topic}".
            Thông tin: {context_text}
            
            Bản tóm tắt nên bao gồm:
            1. Định nghĩa và khái niệm chính
            2. Các điểm quan trọng nhất
            3. Ứng dụng hoặc ý nghĩa thực tiễn
            4. Kết luận ngắn gọn
            
            Hãy viết tóm tắt trong khoảng 300-500 từ, ngắn gọn nhưng đầy đủ thông tin quan trọng."""
            
            response = assistant.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Lỗi khi tạo tóm tắt cho '{topic}': {str(e)}"