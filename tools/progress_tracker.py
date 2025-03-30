from datetime import datetime
from .base_tool import BaseTool

class ProgressTrackerTool(BaseTool):
    @property
    def name(self) -> str:
        return "Progress_Tracker"
    
    @property
    def description(self) -> str:
        return "Theo dõi tiến độ học tập."
    
    def execute(self, assistant, **kwargs):
        input_str = kwargs.get("question", "")
        study_plan = kwargs.get("study_plan", {})
        learning_progress = kwargs.get("learning_progress", {})
        
        return self.track_learning_progress(input_str, study_plan, learning_progress)
    
    def track_learning_progress(self, input_str: str, study_plan: dict, learning_progress: dict) -> str:
        if ":" in input_str:
            subject, progress = input_str.split(":", 1)
            return self.update_learning_progress(subject.strip(), progress.strip(), study_plan, learning_progress)
        
        subject = input_str.strip()
        if not subject:
            result = "Tiến độ học tập hiện tại:\n"
            for subj, data in study_plan.items():
                result += f"- {subj}: {data.get('progress', 0)}%\n"
            for subj, data in learning_progress.items():
                if subj not in study_plan:
                    result += f"- {subj}: {data.get('progress', 0)}%\n"
            return result if len(result) > 25 else "Chưa có dữ liệu tiến độ học tập."
        
        if subject in study_plan:
            progress = study_plan[subject].get("progress", 0)
            created_at = study_plan[subject].get("created_at", "không xác định")
            return f"Tiến độ cho {subject}: {progress}% (Tạo lúc: {created_at})"
        elif subject in learning_progress:
            progress = learning_progress[subject].get("progress", 0)
            updated_at = learning_progress[subject].get("updated_at", "không xác định")
            return f"Tiến độ cho {subject}: {progress}% (Cập nhật lúc: {updated_at})"
        return f"Không tìm thấy tiến độ cho {subject}."
    
    def update_learning_progress(self, subject: str, progress: str, study_plan: dict, learning_progress: dict) -> str:
        if not subject.strip() or not progress.strip():
            return "Vui lòng cung cấp đầy đủ môn học và tiến độ."
        try:
            progress_value = int(progress)
            if progress_value < 0 or progress_value > 100:
                return "Tiến độ phải từ 0 đến 100."
        except ValueError:
            return "Tiến độ phải là số."
        
        data = {"progress": progress_value, "updated_at": datetime.now().isoformat()}
        if subject in study_plan:
            study_plan[subject].update(data)
            return f"Đã cập nhật tiến độ cho {subject}: {progress_value}%"
        else:
            learning_progress[subject] = data
            return f"Đã tạo và cập nhật tiến độ cho {subject}: {progress_value}%"