import re
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from preprocessor import Preprocessor
    from location_parser import LocationParser
    from time_parser import TimeParser
    from habit_parser import HabitParser
except ImportError:
    from nlp.preprocessor import Preprocessor
    from nlp.location_parser import LocationParser
    from nlp.time_parser import TimeParser
    from nlp.habit_parser import HabitParser

class NLPEngine:
    def __init__(self):
        print("⚙️ Đang khởi động NLP Engine...")
        self.preprocessor = Preprocessor()
        self.location_parser = LocationParser()
        self.time_parser = TimeParser()
        self.habit_parser = HabitParser()
        
        # DANH SÁCH TỪ RÁC
        # DANH SÁCH TỪ RÁC (Đã lọc bớt các động từ quan trọng)
        # CHÚ Ý: Đã XÓA 'đi', 'tập', 'chơi' để giữ lại cho tên sự kiện
        self.trash_words = [
            "ở", "tại", "trong", "ngoài", "trên", "dưới", "về", "đến", "tới", 
            "lúc", "vào", "hôm", "ngày", "sáng", "trưa", "chiều", "tối", "đêm",
            "cái", "chiếc", "nha", "nhé", "luôn", "thôi", "nè", "ạ", "dạ",
            "là", "thì", "mà", "bị", "được", "của", "cho", "với", "cùng",
            "trước", "sau", "tầm", "khoảng", "lúc", "gấp", "nhắc", "báo",
            "từ", "sớm", "mất", "qua", "tôi", "có", "hãy", "giúp",
            "đều", "mỗi" # Thêm 'mỗi' để xóa trong 'mỗi tuần'
        ]

    def _remove_substring(self, text, substr):
        if not substr: return text
        pattern = re.escape(substr)
        return re.sub(pattern, " ", text, flags=re.IGNORECASE).strip()

    def _remove_time_patterns(self, text):
        patterns = [
            # 1. Giờ
            r"(?:\b(?:trước|sau|tầm|khoảng|lúc|vào|sớm|từ|đến|kéo dài|trong)\s+)?\d{1,2}\s*(?:h|:|g|giờ)\s*\d{0,2}(?:\s*(?:sáng|trưa|chiều|tối|đêm))?(?:\s*kém\s*\d+)?(?:\s*rưỡi)?",
            r"\bkém\s*\d+(?:\s*(?:phút|p))?",
            
            # 2. Ngày tương đối
            r"\b(?:hôm nay|bữa nay|ngày mai|sáng mai|chiều mai|tối mai|mốt|kia|hôm qua)\b",
            r"\b(?:tuần sau|tháng sau|năm sau)\b",
            
            # 3. [FIX QUAN TRỌNG] Từ đơn chỉ thời gian
            # Logic mới: (?<!buổi\s) nghĩa là: Nếu trước nó là chữ 'buổi' thì KHÔNG XÓA.
            r"(?<!buổi\s)\b(?:mai|nay|sáng|trưa|chiều|tối|đêm)\b",
            
            # 4. Thứ
            r"\b(?:thứ|chủ nhật)\s+(?:\d+|hai|ba|tư|năm|sáu|bảy)\b",
            
            # 5. Khoảng thời gian
            r"\b(?:nãy giờ|tới giờ|ban nãy|lát nữa|sắp tới)\b",
            r"\b\d+\s*(?:tiếng|phút|p)\b",
            
            # 6. Reminder
            r"(?:nhắc|báo|gọi|alarm|nhac|bao)\s*(?:tôi|mình|me)?\s*(?:trước|sớm|lại|truoc|som|\s)*\d+(?:\.\d+)?\s*(?:phút|p|ph|tiếng|giờ|h|g)"
        ]
        
        cleaned_text = text
        for pat in patterns:
            cleaned_text = re.sub(pat, " ", cleaned_text, flags=re.IGNORECASE)
        return cleaned_text.strip()
        
       
        
      

    def _clean_event_name(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()
        if not words: return ""
        
        # Xóa rác đầu câu
        while words and words[0].lower() in self.trash_words:
            words.pop(0)
            if not words: return ""
            
        # Xóa rác cuối câu
        while words and words[-1].lower() in self.trash_words:
            words.pop()
            if not words: return ""
            
        return " ".join(words)

    def extract_event_name(self, text, location):
        current_text = text
        if location:
            current_text = self._remove_substring(current_text, location)
        current_text = self._remove_time_patterns(current_text)
        return self._clean_event_name(current_text) or "Sự kiện mới"

    def process_command(self, raw_text):
        clean_text = self.preprocessor.process(raw_text)
        
        # Habit Parser (Nhớ dùng bản mới nhất em gửi ở tin trước để ưu tiên Weekly)
        habit_info = self.habit_parser.parse(clean_text)
        working_text = habit_info['remaining_text']
        
        location = self.location_parser.extract(working_text)
        time_data = self.time_parser.parse(working_text)
        event_name = self.extract_event_name(working_text, location)
        
        intent = "create_habit" if habit_info['is_habit'] else "create_event"
        
        return {
            "intent": intent,
            "processed_text": clean_text,
            "data": {
                "event_name": event_name,
                "location": location,
                "time": time_data, 
                "habit": habit_info['frequency'],
                "reminder": time_data.get('reminder_minutes')
            }
        }