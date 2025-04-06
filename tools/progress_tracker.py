import logging
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from .base_tool import BaseTool
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
import os
import hashlib
import json
from utils.user_data_manager import UserDataManager  # Import UserDataManager

if TYPE_CHECKING:
    from core.learning_assistant_v2 import LearningAssistant

logger = logging.getLogger(__name__)

# MongoDB Configuration (Consistent with StudyPlanCreatorTool)
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB_NAME = "edumentor"
MONGO_COLLECTION_NAME = "stats" # Collection mới đã tạo
DEFAULT_USER_ID = "anonymous_user" # Sử dụng ID mặc định

class ProgressTrackerTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.mongo_client = None
        self.db = None
        self.collection = None
        self._connect_mongo()
        # Khởi tạo UserDataManager
        self.user_data_manager = UserDataManager()

    def _connect_mongo(self):
        """Establishes connection to MongoDB."""
        if not self.mongo_client:
            try:
                self.mongo_client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)
                self.mongo_client.admin.command('ismaster') 
                self.db = self.mongo_client[MONGO_DB_NAME]
                self.collection = self.db[MONGO_COLLECTION_NAME]
                logger.info(f"ProgressTrackerTool: Successfully connected to MongoDB.")
            except ConnectionFailure:
                logger.error(f"ProgressTrackerTool: Failed to connect to MongoDB. Stats feature will be unavailable.")
                self.mongo_client = None
            except Exception as e:
                 logger.error(f"ProgressTrackerTool: An unexpected error occurred during MongoDB connection: {e}")
                 self.mongo_client = None

    @property
    def name(self) -> str:
        return "Progress_Tracker"

    @property
    def description(self) -> str:
        return "Theo dõi hoặc cập nhật tiến độ học tập và tài liệu của người dùng."

    @property
    def needs_context(self) -> bool:
        """Progress tracker doesn't need document context."""
        return False

    async def execute(self, assistant: 'LearningAssistant', **kwargs) -> Union[str, Dict[str, Any]]:
        input_data = kwargs.get("question", "")
        options = kwargs.get("options", {})
        
        # Lấy username từ options 
        username = options.get("username", "").strip()
        
        # Log để debug thông tin người dùng
        if username:
            logger.info(f"ProgressTrackerTool: Executing with authenticated user: {username}")
        else:
            logger.warning(f"ProgressTrackerTool: No username provided in options, using default: {DEFAULT_USER_ID}")
            username = DEFAULT_USER_ID
        
        # Kiểm tra xem có thể lưu dữ liệu
        save_to_db = self.user_data_manager.is_connected()
        
        if not save_to_db:
            # Thêm cảnh báo nếu không thể kết nối CSDL
            logger.warning("Database not available, operation will not persist data")
            return "Lỗi: Không thể kết nối đến cơ sở dữ liệu."

        # Kiểm tra nếu input là JSON object hoặc dict
        try:
            input_json = None
            input_str = ""
            
            # Xác định kiểu dữ liệu của input
            if isinstance(input_data, dict):
                logger.info("Input is already a dictionary")
                input_json = input_data
            elif isinstance(input_data, str):
                input_str = input_data.strip()
                # Thử parse nếu là JSON format từ UI
                if input_str.startswith('{') and input_str.endswith('}'):
                    try:
                        input_json = json.loads(input_str)
                        logger.info("Successfully parsed JSON string input")
                    except json.JSONDecodeError:
                        logger.info("Input is not a valid JSON string, treating as plain text")

            # Nếu là JSON object với subject và progress
            if input_json and isinstance(input_json, dict):
                logger.info(f"Processing JSON input: {input_json}")
                if 'subject' in input_json and 'progress' in input_json:
                    subject = input_json['subject']
                    progress_value = input_json['progress']
                    
                    if not subject:
                        return "Lỗi: Tên môn học không được để trống khi cập nhật tiến độ."
                    
                    # Validate progress
                    if not isinstance(progress_value, (int, float)):
                        try:
                            progress_value = int(progress_value)
                        except (ValueError, TypeError):
                            return "Lỗi: Tiến độ phải là một số từ 0 đến 100."
                    
                    progress_value = int(progress_value)
                    if not (0 <= progress_value <= 100):
                        return "Lỗi: Tiến độ phải là một số từ 0 đến 100."
                    
                    # Update progress using UserDataManager
                    logger.info(f"Updating progress for '{subject}' to {progress_value}% for user '{username}'")
                    success = self.user_data_manager.update_progress(username, subject, progress_value)
                    if success:
                        return {"success": True, "message": f"Đã cập nhật tiến độ cho '{subject}' thành {progress_value}%."}
                    else:
                        return {"success": False, "message": f"Không thể cập nhật tiến độ cho '{subject}'."}
                return {"success": False, "message": "Format không hợp lệ. Cần có 'subject' và 'progress'."}
        except Exception as e:
            logger.error(f"Error processing input data: {e}")
            # Tiếp tục xử lý như input thông thường
            
        # Xử lý như văn bản thông thường nếu không phải JSON
        if isinstance(input_data, str):
            input_str = input_data.strip()
            # Xử lý các command đặc biệt (định dạng cũ)
            if input_str.startswith("upload:"):
                # Xử lý thông tin tài liệu upload
                _, params = input_str.split(":", 1)
                return self._process_document_upload(username, params.strip())
            elif input_str.startswith("documents:"):
                # Liệt kê tài liệu của một môn học hoặc tất cả các môn
                _, subject = input_str.split(":", 1)
                return self._list_documents(username, subject.strip())
            elif ":" in input_str and not any(input_str.startswith(cmd) for cmd in ["upload:", "documents:"]):
                # Cập nhật tiến độ (định dạng cũ)
                try:
                    subject, progress_str = input_str.split(":", 1)
                    subject = subject.strip()
                    progress_str = progress_str.strip()
                    if not subject:
                        return "Lỗi: Tên môn học không được để trống khi cập nhật tiến độ."
                    # Validate progress value
                    try:
                        progress_value = int(progress_str)
                        if not (0 <= progress_value <= 100):
                            return "Lỗi: Tiến độ phải là một số từ 0 đến 100."
                    except ValueError:
                        return "Lỗi: Tiến độ cung cấp không phải là một số hợp lệ."
                        
                    # Update progress in MongoDB using UserDataManager
                    success = self.user_data_manager.update_progress(username, subject, progress_value)
                    if success:
                        return {"success": True, "message": f"Đã cập nhật tiến độ cho '{subject}' thành {progress_value}%."}
                    else:
                        return {"success": False, "message": f"Không thể cập nhật tiến độ cho '{subject}'."}
                except ValueError:
                    return {"success": False, "message": "Lỗi: Định dạng cập nhật tiến độ không hợp lệ. Sử dụng 'Môn học: <tiến độ%>'."}
            else:
                # Retrieve progress from MongoDB
                subject_to_get = input_str # If empty, gets all; otherwise, gets specific subject
                result = self._get_progress_from_db(username, subject_to_get)
                if isinstance(result, str):
                    return {"success": True, "response": result}
                return result
        else:
            # Input không phải string và không phải JSON hợp lệ
            return {"success": False, "message": "Định dạng đầu vào không hợp lệ. Vui lòng sử dụng văn bản hoặc JSON."}

    def _process_document_upload(self, username: str, params: str) -> str:
        """
        Xử lý thông tin tài liệu đã upload và cập nhật vào cơ sở dữ liệu
        
        Format: upload:filename.pdf|subject|page_count|size_bytes
        Ví dụ: upload:dai_so.pdf|Toán học|45|1024000
        """
        try:
            parts = params.split('|')
            if len(parts) < 2:
                return "Lỗi: Thiếu thông tin. Định dạng: upload:filename.pdf|môn học|số trang|kích thước"
            
            filename = parts[0].strip()
            subject = parts[1].strip()
            
            # Thông tin tùy chọn
            page_count = int(parts[2]) if len(parts) > 2 and parts[2].strip() else None
            size_bytes = int(parts[3]) if len(parts) > 3 and parts[3].strip() else None
            
            # Sử dụng UserDataManager để thêm tài liệu
            document_id = self.user_data_manager.add_document(
                username, subject, filename, page_count, size_bytes
            )
            
            if document_id:
                return f"Đã thêm tài liệu '{filename}' vào môn học '{subject}' thành công."
            else:
                return f"Không thể thêm tài liệu '{filename}' (có thể đã tồn tại hoặc có lỗi xảy ra)."
                
        except Exception as e:
            logger.exception(f"Error processing document upload: {e}")
            return f"Lỗi xử lý thông tin tài liệu: {str(e)}"

    def _list_documents(self, username: str, subject: str = "") -> str:
        """Liệt kê các tài liệu đã upload của người dùng."""
        try:
            # Sử dụng UserDataManager để lấy danh sách tài liệu
            if subject:
                # Liệt kê tài liệu của một môn học cụ thể
                documents = self.user_data_manager.get_documents(username, subject)
                
                if not documents:
                    return f"Không có tài liệu nào trong môn học '{subject}'."
                    
                result_lines = [f"Tài liệu môn {subject}:"]
                for i, doc in enumerate(documents, 1):
                    filename = doc.get("filename", "Không có tên")
                    upload_date = doc.get("upload_date")
                    upload_date_str = upload_date.strftime("%Y-%m-%d") if upload_date else "N/A"
                    page_count = doc.get("page_count", "N/A")
                    
                    result_lines.append(f"{i}. {filename} - Ngày upload: {upload_date_str} - Số trang: {page_count}")
                
                return "\n".join(result_lines)
            else:
                # Liệt kê tài liệu của tất cả các môn học
                documents = self.user_data_manager.get_documents(username)
                
                if not documents:
                    return "Không có tài liệu nào được upload."
                    
                # Nhóm tài liệu theo môn học
                docs_by_subject = {}
                for doc in documents:
                    subject_name = doc.get("subject", "Không rõ môn học")
                    if subject_name not in docs_by_subject:
                        docs_by_subject[subject_name] = []
                    docs_by_subject[subject_name].append(doc)
                
                result_lines = ["Danh sách tất cả tài liệu:"]
                for subject_name, subject_docs in sorted(docs_by_subject.items()):
                    result_lines.append(f"\nMôn {subject_name}:")
                    for i, doc in enumerate(subject_docs, 1):
                        filename = doc.get("filename", "Không có tên")
                        upload_date = doc.get("upload_date")
                        upload_date_str = upload_date.strftime("%Y-%m-%d") if upload_date else "N/A"
                        
                        result_lines.append(f"{i}. {filename} - Ngày upload: {upload_date_str}")
                
                return "\n".join(result_lines)
                
        except Exception as e:
            logger.exception(f"Error listing documents: {e}")
            return f"Lỗi khi liệt kê tài liệu: {str(e)}"

    def _get_progress_from_db(self, username: str, subject: str = "") -> str:
        """Truy xuất tiến độ từ cơ sở dữ liệu. Lấy tất cả nếu subject rỗng."""
        try:
            if subject:
                # Lấy thông tin về một môn học cụ thể
                stats = self.user_data_manager.get_user_stats(username, subject)
                if subject not in stats or not stats[subject]:
                    return f"Không tìm thấy dữ liệu tiến độ cho môn học '{subject}'."
                
                subject_data = stats[subject]
                progress = subject_data.get("progress", "Chưa có")
                updated_at_utc = subject_data.get("progress_updated_at")
                updated_at_str = updated_at_utc.strftime('%Y-%m-%d %H:%M:%S UTC') if updated_at_utc else "Chưa cập nhật"
                plan_created_at_utc = subject_data.get("plan_created_at")
                plan_created_at_str = plan_created_at_utc.strftime('%Y-%m-%d %H:%M:%S UTC') if plan_created_at_utc else "Chưa có"
                
                # Thêm thông tin số lượng tài liệu
                documents = subject_data.get("documents", [])
                doc_count = len(documents)
                doc_info = f"Số tài liệu: {doc_count}" if doc_count > 0 else "Chưa có tài liệu"

                return (f"Tiến độ cho '{subject}': {progress}%\n"
                        f"  Cập nhật lần cuối: {updated_at_str}\n"
                        f"  {doc_info}\n"
                        f"  Kế hoạch tạo lúc: {plan_created_at_str}")
            else:
                # Lấy thông tin về tất cả các môn học
                stats = self.user_data_manager.get_user_stats(username)
                
                if not stats:
                     return f"Chưa có dữ liệu tiến độ nào được ghi nhận. Vui lòng cập nhật tiến độ cho một môn học."
                     
                result_lines = [f"Tiến độ học tập:"]
                for subj, data in sorted(stats.items()):
                    prog = data.get("progress", "N/A")
                    updated_at_utc = data.get("progress_updated_at")
                    updated_at_str = updated_at_utc.strftime('%Y-%m-%d') if updated_at_utc else "N/A"
                    doc_count = len(data.get("documents", []))
                    doc_info = f", {doc_count} tài liệu" if doc_count > 0 else ""
                    result_lines.append(f"- {subj}: {prog}% (Cập nhật: {updated_at_str}{doc_info})")
                
                # Thêm thông tin hoạt động gần đây
                recent_activities = self.user_data_manager.get_recent_activities(username, limit=5)
                if recent_activities:
                    result_lines.append("\nHoạt động gần đây:")
                    for i, activity in enumerate(recent_activities, 1):
                        action = activity.get("action", "")
                        timestamp = activity.get("timestamp")
                        timestamp_str = timestamp.strftime('%Y-%m-%d') if timestamp else "N/A"
                        subject = activity.get("subject", "")
                        document = activity.get("document", "")
                        
                        if action == "upload":
                            act_str = f"Upload tài liệu '{document}' vào môn {subject}"
                        elif action == "update_progress":
                            progress = activity.get("progress", "")
                            act_str = f"Cập nhật tiến độ môn {subject}: {progress}%"
                        elif action == "learn":
                            duration = activity.get("duration_minutes", "")
                            act_str = f"Học môn {subject} ({duration} phút)"
                        elif action == "create_plan":
                            act_str = f"Tạo kế hoạch học tập cho môn {subject}"
                        else:
                            act_str = f"Hoạt động: {action}"
                            
                        result_lines.append(f"{i}. {timestamp_str}: {act_str}")
                
                return "\n".join(result_lines)

        except Exception as e:
            logger.exception(f"Error getting progress from database: {e}")
            return f"Lỗi: Đã xảy ra lỗi không mong muốn khi truy xuất tiến độ: {str(e)}"

    def record_learning_activity(self, username: str, subject: str, document_id: Optional[str] = None, 
                               duration_minutes: int = 0, topics: List[str] = None) -> bool:
        """
        Ghi lại hoạt động học tập của người dùng
        
        Args:
            username: Tên người dùng
            subject: Môn học
            document_id: ID của tài liệu học (tùy chọn)
            duration_minutes: Thời gian học (phút)
            topics: Danh sách các chủ đề đã học
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        if not self.collection:
            logger.error("Cannot record learning activity: No database connection")
            return False
            
        try:
            now_utc = datetime.now(timezone.utc)
            topics = topics or []
            
            # Tìm thông tin document nếu có document_id
            document_name = None
            if document_id:
                user_data = self.collection.find_one({"_id": username})
                if user_data and "stats" in user_data:
                    for subject_data in user_data["stats"].values():
                        for doc in subject_data.get("documents", []):
                            if doc.get("document_id") == document_id:
                                document_name = doc.get("filename")
                                # Cập nhật last_accessed
                                self.collection.update_one(
                                    {"_id": username, "stats.*.documents.document_id": document_id},
                                    {"$set": {"stats.$.documents.$.last_accessed": now_utc}}
                                )
                                break
            
            # Tạo activity entry
            activity = {
                "action": "learn",
                "subject": subject,
                "timestamp": now_utc,
                "duration_minutes": duration_minutes
            }
            
            if document_name:
                activity["document"] = document_name
                
            # Cập nhật learning history
            learning_entry = {
                "date": now_utc,
                "duration_minutes": duration_minutes,
                "topics": topics
            }
            
            if document_id:
                learning_entry["document_id"] = document_id
                
            # Cập nhật vào database
            result = self.collection.update_one(
                {"_id": username},
                {
                    "$push": {
                        f"stats.{subject}.learning_history": learning_entry,
                        "recent_activities": activity
                    },
                    "$set": {"last_login": now_utc}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.exception(f"Error recording learning activity: {e}")
            return False

    def __del__(self):
        """Ensure MongoDB client is closed when the object is destroyed."""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB client closed for ProgressTrackerTool.")
