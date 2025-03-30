from datetime import datetime
from .base_tool import BaseTool

class MindMapCreatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "Mind_Map_Creator"
    
    @property
    def description(self) -> str:
        return "Tạo sơ đồ tư duy cho một chủ đề."
    
    async def execute(self, assistant, **kwargs):
        topic = kwargs.get("question", "")
        if not topic.strip():
            return "Vui lòng cung cấp chủ đề để tạo sơ đồ tư duy."
        try:
            context = await assistant.retriever.search(topic)
            if not context:
                return f"Không tìm thấy thông tin về '{topic}' để tạo sơ đồ tư duy."
            context_text = "\n\n".join([f"Slide {doc.get('slide_number', 'N/A')}: {doc['text']}" for doc in context])
            prompt = f"""Dựa trên thông tin sau, tạo sơ đồ tư duy cho chủ đề "{topic}".
            Thông tin: {context_text}
            
            Sơ đồ tư duy nên có:
            1. Chủ đề chính ở trung tâm
            2. Các nhánh chính (khái niệm chính)
            3. Các nhánh phụ (khái niệm phụ, kèm số slide nếu có)
            4. Mối quan hệ giữa các khái niệm
            
            Hãy trình bày sơ đồ tư duy dưới dạng văn bản có cấu trúc rõ ràng, sử dụng ký hiệu để thể hiện cấp độ và mối quan hệ."""
            
            response = assistant.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Lỗi khi tạo sơ đồ tư duy cho '{topic}': {str(e)}"