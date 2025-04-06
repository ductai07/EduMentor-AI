import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class EmotionState(Enum):
    """Các trạng thái cảm xúc cơ bản của người học."""
    POSITIVE = "positive"  # Tích cực, hứng thú, hài lòng
    NEUTRAL = "neutral"    # Trung tính
    CONFUSED = "confused"  # Bối rối, không hiểu
    FRUSTRATED = "frustrated"  # Thất vọng, khó chịu
    ANXIOUS = "anxious"    # Lo lắng, căng thẳng
    BORED = "bored"        # Chán nản
    TIRED = "tired"        # Mệt mỏi, kiệt sức
    ANGRY = "angry"        # Tức giận, bực bội
 
class EmotionAnalyzer:
    """Phân tích cảm xúc từ văn bản người dùng."""
    
    def __init__(self):
        # Từ điển các từ khóa cảm xúc và biểu thức cảm xúc
        self.emotion_keywords = {
            EmotionState.POSITIVE: [
                r"\b(thích|tuyệt|hay|tốt|hiểu|rõ|cảm ơn|cám ơn|vui|thú vị|hứng thú|thú vị|tuyệt vời|tuyệt quá|hay quá)\b",
                r"\b(thích thú|rất hay|rất tốt|rất thú vị|rất hứng thú)\b",
                r"\b(\:\)|\:\-\)|\=\))\b",  # Emoji mặt cười
            ],
            EmotionState.CONFUSED: [
                r"\b(không hiểu|khó hiểu|rối|bối rối|lúng túng|mơ hồ|mông lung|không rõ)\b",
                r"\b(là sao|thế nào|như thế nào|tại sao|vì sao|không biết)\b",
                r"\b(\?{2,})\b",  # Nhiều dấu hỏi
            ],
            EmotionState.FRUSTRATED: [
                r"\b(khó|khó quá|phức tạp|rắc rối|không được|thất vọng|chán nản|bực|tức|khó chịu)\b",
                r"\b(không thể|không làm được|không hiểu nổi|quá khó|quá phức tạp)\b",
                r"\b(\:{0,1}\(|\:\-\()\b",  # Emoji mặt buồn
            ],
            EmotionState.ANXIOUS: [
                r"\b(lo|lo lắng|sợ|căng thẳng|áp lực|stress|không kịp|không đủ|gấp)\b",
                r"\b(sắp thi|kỳ thi|deadline|hạn chót|không đủ thời gian)\b",
            ],
            EmotionState.BORED: [
                r"\b(chán|nhàm chán|buồn ngủ|buồn chán|buồn nhỉ|buồn|dài dòng|lê thê|tẻ nhạt)\b",
            ],
            EmotionState.TIRED: [
                r"\b(mệt|mệt mỏi|mệt quá|kiệt sức|không còn sức|đuối|mệt vl|mệt vcl|mệt vãi|mệt đừ|mệt lử)\b",
                r"\b(không còn năng lượng|không muốn làm|không đủ sức|cạn kiệt|không chịu nổi)\b",
                r"\b(muốn nghỉ|cần nghỉ|phải nghỉ|nghỉ ngơi|ngủ quá|buồn ngủ quá)\b",
            ],
            EmotionState.ANGRY: [
                r"\b(tức|tức giận|bực|bực mình|bực bội|cáu|cáu gắt|điên|điên tiết|nổi điên|phát điên)\b",
                r"\b(khó chịu quá|tức quá|bực quá|cáu quá|điên quá|phát điên|nổi điên)\b",
                r"\b(tức chết|tức muốn chết|tức phát khóc|tức ói|tức chết đi được)\b",
                r"\b(đm|đéo|đcm|đcmm|vl|vcl|vãi|vkl|wtf)\b",  # Từ ngữ thô tục thể hiện sự tức giận
            ],
            EmotionState.NEUTRAL: []  # Mặc định nếu không khớp với các cảm xúc khác
        }
        
        # Các mẫu câu thường gặp cho từng trạng thái cảm xúc
        self.emotion_patterns = {
            EmotionState.POSITIVE: [
                r".*\b(hay|tốt|thích|tuyệt)\b.*",
                r".*cảm ơn.*",
            ],
            EmotionState.CONFUSED: [
                r".*không hiểu.*",
                r".*\b(là sao|thế nào)\b.*\?",
                r".*\b(giải thích|làm rõ)\b.*\?",
            ],
            EmotionState.FRUSTRATED: [
                r".*\b(khó quá|không làm được)\b.*",
                r".*\b(thất vọng|chán nản)\b.*",
            ],
            EmotionState.ANXIOUS: [
                r".*\b(lo lắng|sợ|không kịp)\b.*",
                r".*\b(sắp thi|deadline)\b.*",
            ],
            EmotionState.BORED: [
                r".*\b(chán|nhàm chán)\b.*",
            ],
            EmotionState.TIRED: [
                r".*\b(mệt|mệt quá|kiệt sức)\b.*",
                r".*\b(mệt vl|mệt vcl|mệt vãi)\b.*",
                r".*\b(không còn sức|đuối|cạn kiệt)\b.*",
                r".*\b(muốn nghỉ|cần nghỉ)\b.*",
            ],
            EmotionState.ANGRY: [
                r".*\b(tức|bực|cáu|điên)\b.*",
                r".*\b(tức quá|bực quá|cáu quá)\b.*",
                r".*\b(đm|đéo|vl|vcl|vãi)\b.*",
            ],
        }
    
    def detect_emotion(self, text: str) -> Tuple[EmotionState, float]:
        """Phát hiện trạng thái cảm xúc từ văn bản.
        
        Args:
            text: Văn bản cần phân tích
            
        Returns:
            Tuple chứa trạng thái cảm xúc và độ tin cậy
        """
        if not text or not isinstance(text, str):
            return EmotionState.NEUTRAL, 0.5
        
        text = text.lower()
        emotion_scores = {emotion: 0.0 for emotion in EmotionState}
        
        # Phân tích dựa trên từ khóa
        for emotion, patterns in self.emotion_keywords.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    emotion_scores[emotion] += len(matches) * 0.2
        
        # Phân tích dựa trên mẫu câu
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                if re.match(pattern, text):
                    emotion_scores[emotion] += 0.3
        
        # Nếu không có cảm xúc nào được phát hiện, mặc định là trung tính
        if all(score == 0 for emotion, score in emotion_scores.items()):
            return EmotionState.NEUTRAL, 0.5
        
        # Tìm cảm xúc có điểm cao nhất
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        confidence = min(max_emotion[1], 1.0)  # Giới hạn độ tin cậy tối đa là 1.0
        
        return max_emotion[0], confidence

class ResponseAdjuster:
    """Điều chỉnh phản hồi dựa trên trạng thái cảm xúc."""
    
    def __init__(self):
        # Các mẫu câu hỗ trợ cho từng trạng thái cảm xúc
        self.support_templates = {
            EmotionState.POSITIVE: [
                "Tôi rất vui khi bạn thấy hứng thú với nội dung này!",
                "Thật tuyệt khi bạn đang tiến bộ!",
                "Cảm ơn bạn đã chia sẻ phản hồi tích cực!",
            ],
            EmotionState.CONFUSED: [
                "Tôi hiểu rằng điều này có thể hơi khó hiểu. Hãy cùng chia nhỏ vấn đề:",
                "Đừng lo lắng nếu bạn cảm thấy bối rối. Tôi sẽ giải thích rõ hơn:",
                "Tôi sẽ cố gắng giải thích theo cách dễ hiểu hơn:",
            ],
            EmotionState.FRUSTRATED: [
                "Tôi hiểu cảm giác thất vọng của bạn. Hãy thử cách tiếp cận khác:",
                "Đừng nản lòng! Nhiều người cũng gặp khó khăn với phần này. Hãy thử:",
                "Tôi biết điều này có thể gây khó chịu. Hãy chia nhỏ vấn đề và giải quyết từng bước:",
            ],
            EmotionState.ANXIOUS: [
                "Tôi hiểu bạn đang cảm thấy áp lực. Hãy thở sâu và cùng giải quyết từng bước một:",
                "Lo lắng là bình thường, nhưng bạn đang làm rất tốt! Hãy tập trung vào:",
                "Đừng quá lo lắng. Chúng ta sẽ giải quyết vấn đề này cùng nhau:",
            ],
            EmotionState.BORED: [
                "Hãy thử cách tiếp cận thú vị hơn với chủ đề này:",
                "Tôi hiểu rằng đôi khi nội dung có thể hơi khô khan. Hãy thử kết nối nó với:",
                "Hãy thử áp dụng kiến thức này vào một tình huống thực tế thú vị:",
            ],
            EmotionState.TIRED: [
                "Tôi nhận thấy bạn đang cảm thấy mệt mỏi. Hãy xem xét nghỉ ngơi một chút:",
                "Sự mệt mỏi có thể ảnh hưởng đến hiệu quả học tập. Hãy thử chia nhỏ nội dung:",
                "Tôi hiểu cảm giác kiệt sức của bạn. Đây là cách tiếp cận nhẹ nhàng hơn:",
            ],
            EmotionState.ANGRY: [
                "Tôi hiểu bạn đang cảm thấy bực bội. Hãy thử cách tiếp cận khác:",
                "Sự tức giận đôi khi là phản ứng tự nhiên khi gặp khó khăn. Hãy thử:",
                "Tôi thấy bạn đang khó chịu. Hãy cùng giải quyết vấn đề một cách bình tĩnh:",
            ],
            EmotionState.NEUTRAL: [
                "",  # Không thêm gì đặc biệt cho trạng thái trung tính
            ],
        }
        
        # Các mẫu câu kết thúc cho từng trạng thái cảm xúc
        self.closing_templates = {
            EmotionState.POSITIVE: [
                "Hãy tiếp tục phát huy nhé!",
                "Bạn đang làm rất tốt!",
                "Tiếp tục với tinh thần tích cực nhé!",
            ],
            EmotionState.CONFUSED: [
                "Bạn có thắc mắc gì thêm không? Tôi luôn sẵn sàng giải thích rõ hơn.",
                "Nếu vẫn còn điểm nào chưa rõ, đừng ngại hỏi lại nhé.",
                "Hãy cho tôi biết nếu bạn cần giải thích thêm về bất kỳ phần nào.",
            ],
            EmotionState.FRUSTRATED: [
                "Đừng nản lòng! Mỗi thử thách đều giúp bạn tiến bộ hơn.",
                "Hãy kiên nhẫn với bản thân. Bạn sẽ vượt qua được thử thách này!",
                "Tôi tin bạn có thể làm được. Hãy thử lại nhé!",
            ],
            EmotionState.ANXIOUS: [
                "Hãy nhớ rằng, quá trình học tập quan trọng hơn kết quả cuối cùng.",
                "Bạn đang làm tốt hơn bạn nghĩ đấy. Hãy tin vào khả năng của mình!",
                "Đừng quên dành thời gian nghỉ ngơi để tái tạo năng lượng nhé.",
            ],
            EmotionState.BORED: [
                "Hy vọng cách tiếp cận này sẽ làm bạn hứng thú hơn với chủ đề!",
                "Thử áp dụng kiến thức này vào sở thích của bạn xem sao!",
                "Đôi khi, kết nối kiến thức với thực tế sẽ làm mọi thứ thú vị hơn nhiều!",
            ],
            EmotionState.TIRED: [
                "Đừng quên nghỉ ngơi là một phần quan trọng của quá trình học tập hiệu quả.",
                "Hãy dành thời gian nghỉ ngơi đầy đủ. Não bộ cần thời gian để xử lý thông tin mới.",
                "Kỹ thuật Pomodoro (học 25 phút, nghỉ 5 phút) có thể giúp bạn duy trì năng lượng tốt hơn.",
            ],
            EmotionState.ANGRY: [
                "Hãy thử lùi lại một bước và nhìn vấn đề từ góc độ khác. Đôi khi điều đó giúp giảm căng thẳng.",
                "Sự tức giận có thể là động lực nếu được chuyển hóa đúng cách. Hãy thử chuyển nó thành quyết tâm!",
                "Đừng ngại nghỉ giải lao nếu cảm thấy quá bực bội. Một tâm trí bình tĩnh sẽ giải quyết vấn đề tốt hơn.",
            ],
            EmotionState.NEUTRAL: [
                "Bạn có câu hỏi nào khác không?",
                "Tôi hy vọng thông tin này hữu ích cho bạn.",
                "Hãy cho tôi biết nếu bạn cần thêm thông tin.",
            ],
        }
    
    def adjust_response(self, response: str, emotion: EmotionState, confidence: float, 
                        add_support_prefix: bool = True, add_closing: bool = True) -> str:
        """Điều chỉnh phản hồi dựa trên trạng thái cảm xúc.
        
        Args:
            response: Phản hồi gốc
            emotion: Trạng thái cảm xúc đã phát hiện
            confidence: Độ tin cậy của phát hiện cảm xúc
            add_support_prefix: Có thêm câu hỗ trợ ở đầu không
            add_closing: Có thêm câu kết thúc không
            
        Returns:
            Phản hồi đã được điều chỉnh
        """
        import random
        
        # Nếu độ tin cậy thấp, không điều chỉnh
        if confidence < 0.3 or emotion == EmotionState.NEUTRAL:
            return self._format_response(response)
        
        adjusted_response = []
        
        # Thêm câu hỗ trợ ở đầu nếu cần
        if add_support_prefix and emotion != EmotionState.NEUTRAL:
            support_templates = self.support_templates.get(emotion, [])
            if support_templates:
                adjusted_response.append(random.choice(support_templates))
        
        # Thêm phản hồi gốc
        adjusted_response.append(response)
        
        # Thêm câu kết thúc nếu cần
        if add_closing and emotion != EmotionState.NEUTRAL:
            closing_templates = self.closing_templates.get(emotion, [])
            if closing_templates:
                adjusted_response.append(random.choice(closing_templates))
        
        # Kết hợp và định dạng phản hồi
        return self._format_response("\n\n".join(adjusted_response))
    
    def _format_response(self, response: str) -> str:
        """Định dạng phản hồi để hiển thị clean hơn."""
        if not response:
            return ""
            
        # Đảm bảo xuống dòng đúng cách
        response = re.sub(r'\n{3,}', '\n\n', response)  # Giảm nhiều dòng trống thành tối đa 2
        response = re.sub(r'\s+\n', '\n', response)  # Loại bỏ khoảng trắng ở cuối dòng
        response = re.sub(r'\n\s+', '\n', response)  # Loại bỏ khoảng trắng ở đầu dòng
        
        # Đảm bảo định dạng markdown hiển thị đúng
        response = re.sub(r'\*\*(.*?)\*\*', r'**\1**', response)  # Đảm bảo in đậm hiển thị đúng
        
        # Đảm bảo các đoạn văn được phân tách rõ ràng
        paragraphs = [p.strip() for p in response.split('\n\n')]
        clean_paragraphs = [p for p in paragraphs if p]
        
        # Đảm bảo các dấu xuống dòng trong danh sách được giữ nguyên
        formatted_response = "\n\n".join(clean_paragraphs)
        formatted_response = re.sub(r'(\d+\.)\s*\n\s*', r'\1 ', formatted_response)
        
        return formatted_response

class MotivationalSupport:
    """Cung cấp hỗ trợ động lực dựa trên trạng thái cảm xúc."""
    
    def __init__(self):
        # Các mẫu câu động viên cho từng trạng thái cảm xúc
        self.motivational_messages = {
            EmotionState.CONFUSED: [
                "Sự bối rối là một phần tự nhiên của quá trình học tập. Einstein từng nói: 'Nếu bạn không thể giải thích điều gì đó một cách đơn giản, bạn chưa hiểu nó đủ rõ.'",
                "Mỗi câu hỏi đều đáng giá. Socrates đã xây dựng cả phương pháp triết học dựa trên việc đặt câu hỏi!",
                "Khi bạn cảm thấy bối rối, đó chính là lúc não bạn đang cố gắng kết nối các ý tưởng mới. Đây là dấu hiệu của sự phát triển!",
            ],
            EmotionState.FRUSTRATED: [
                "Thomas Edison thử nghiệm hơn 1,000 cách trước khi phát minh ra bóng đèn. Ông nói: 'Tôi không thất bại. Tôi chỉ tìm ra 1,000 cách không hoạt động.'",
                "Mỗi thử thách đều là cơ hội để phát triển. Carol Dweck gọi đây là 'tư duy phát triển' - niềm tin rằng khả năng có thể phát triển qua nỗ lực.",
                "Đôi khi, bước lùi một bước sẽ giúp bạn nhìn thấy bức tranh tổng thể rõ ràng hơn. Hãy thử nghỉ ngơi một chút và quay lại với góc nhìn mới.",
            ],
            EmotionState.ANXIOUS: [
                "Lo lắng là phản ứng tự nhiên khi bạn quan tâm đến kết quả. Hãy chuyển năng lượng đó thành động lực để chuẩn bị tốt hơn.",
                "Kỹ thuật '5-4-3-2-1': Hãy nhận biết 5 điều bạn thấy, 4 điều bạn cảm nhận, 3 điều bạn nghe, 2 điều bạn ngửi và 1 điều bạn nếm. Điều này giúp đưa bạn về hiện tại.",
                "Hãy nhớ rằng, căng thẳng vừa phải thực sự có thể cải thiện hiệu suất. Đó là 'vùng học tập tối ưu' của bạn!",
            ],
            EmotionState.BORED: [
                "Albert Einstein phát triển thuyết tương đối khi đang làm việc tại văn phòng cấp bằng sáng chế - một công việc khá nhàm chán! Đôi khi, sự nhàm chán có thể dẫn đến những ý tưởng đột phá.",
                "Thử thách bản thân: Đặt ra một mục tiêu nhỏ hoặc biến nó thành một trò chơi. Não bộ của chúng ta thích những thử thách vừa phải.",
                "Kết nối kiến thức với sở thích cá nhân của bạn. Làm thế nào bạn có thể áp dụng những gì đang học vào điều bạn đam mê?",
            ],
            EmotionState.TIRED: [
                "Nghiên cứu cho thấy rằng học tập ngắn và tập trung (20-30 phút) với thời gian nghỉ ngơi giữa các phiên có thể hiệu quả hơn nhiều so với học liên tục trong thời gian dài.",
                "Leonardo da Vinci thực hành 'giấc ngủ đa pha' - ngủ 20 phút mỗi 4 giờ - để tối đa hóa sáng tạo và năng suất. Một giấc ngủ ngắn có thể làm mới não bộ của bạn!",
                "Theo nghiên cứu của Đại học Harvard, thiếu ngủ có thể làm giảm khả năng ghi nhớ đến 40%. Nghỉ ngơi đầy đủ không phải là lãng phí thời gian mà là đầu tư cho hiệu suất học tập.",
            ],
            EmotionState.ANGRY: [
                "Aristotle từng nói: 'Bất kỳ ai cũng có thể tức giận - điều đó rất dễ. Nhưng tức giận với đúng người, đúng mức độ, đúng thời điểm, đúng mục đích và đúng cách - điều đó không dễ dàng.'",
                "Nghiên cứu tâm lý học cho thấy rằng viết ra những suy nghĩ và cảm xúc tiêu cực có thể giúp giảm cường độ của chúng. Thử dành 5 phút viết ra những gì đang làm bạn bực bội.",
                "Kỹ thuật 'tạm dừng nhận thức': Khi cảm thấy tức giận, hãy đếm đến 10 trước khi phản ứng. Điều này cho phép vỏ não trước trán của bạn (phần hợp lý của não) bắt kịp hệ thống limbic (phần cảm xúc).",
            ],
        }
    
    def get_motivational_support(self, emotion: EmotionState, confidence: float) -> Optional[str]:
        """Lấy thông điệp động viên dựa trên trạng thái cảm xúc.
        
        Args:
            emotion: Trạng thái cảm xúc đã phát hiện
            confidence: Độ tin cậy của phát hiện cảm xúc
            
        Returns:
            Thông điệp động viên hoặc None nếu không cần
        """
        import random
        
        # Chỉ cung cấp hỗ trợ động lực cho các trạng thái cảm xúc tiêu cực với độ tin cậy cao
        if emotion in [EmotionState.CONFUSED, EmotionState.FRUSTRATED, 
                      EmotionState.ANXIOUS, EmotionState.BORED,
                      EmotionState.TIRED, EmotionState.ANGRY] and confidence >= 0.5:
            messages = self.motivational_messages.get(emotion, [])
            if messages:
                return random.choice(messages)
        
        return None