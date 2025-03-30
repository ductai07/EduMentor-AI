from datetime import datetime
from .base_tool import BaseTool

class StudyPlanCreatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "Study_Plan_Creator"
    
    @property
    def description(self) -> str:
        return "Tạo kế hoạch học tập cho một chủ đề."
    
    async def execute(self, assistant, **kwargs):
        subject = kwargs.get("question", "")
        study_plan = kwargs.get("study_plan", {})
        
        if not subject.strip():
            return "Vui lòng cung cấp chủ đề để tạo kế hoạch học tập."
        
        try:
            context = await assistant.retriever.search(subject)
            if not context:
                return f"Không tìm thấy thông tin về '{subject}' để tạo kế hoạch học tập."
                
            context_text = "\n\n".join([doc["text"] for doc in context])
            prompt = f"""Dựa trên thông tin sau, tạo kế hoạch học tập chi tiết cho chủ đề "{subject}".
            Thông tin: {context_text}
            Kế hoạch bao gồm: mục tiêu, các chủ đề con, thời gian, tài nguyên, bài tập, đánh giá tiến độ."""
            
            response = assistant.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Lưu kế hoạch học tập
            study_plan[subject] = {
                "plan": content, 
                "created_at": datetime.now().isoformat(), 
                "progress": 0
            }
            
            return content
        except Exception as e:
            return f"Lỗi khi tạo kế hoạch học tập cho '{subject}': {str(e)}"