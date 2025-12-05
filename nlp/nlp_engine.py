import re
import sys
import os
import unicodedata
from datetime import datetime
from typing import Dict, Any, Optional, List

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
    """Engine xử lý NLP: Trích xuất intent, thời gian, địa điểm và tên sự kiện từ câu đầu vào."""
    
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.location_parser = LocationParser()
        self.time_parser = TimeParser()
        self.habit_parser = HabitParser()
        
        # Danh sách từ rác (stopwords)
        self.trash_words = [
            "ở", "tại", "trong", "ngoài", "trên", "dưới", 
            "lúc", "vào", "hôm", "ngày", "sáng", "trưa", "chiều", "tối", "đêm",
            "cái", "chiếc", "nha", "nhé", "luôn", "thôi", "nè", "ạ", "dạ",
            "là", "thì", "mà", "bị", "được", "của", "cho", "với", "cùng",
            "trước", "sau", "tầm", "khoảng", "gấp", "nhắc", "báo", "báo thức",
            "từ", "sớm", "mất", "qua", "tôi", "có", "hãy", "giúp", "để", "nhờ",
            "đều", "mỗi", "cũng", "vẫn", "còn", "rồi", "nữa", "lại", "mình", "bạn", "em", "anh"
        ]
        self.priority_verbs = ["đi", "về", "ăn", "ngủ", "học", "chơi", "làm", "đá", "xem", "coi", "mua", "bán", "gặp"]

    def _remove_substring(self, text: str, substr: str) -> str:
        """Xóa substring từ text (kèm giới từ đứng trước)."""
        if not substr:
            return text
        # Regex xóa: (giới từ tùy chọn) + (địa điểm)
        preps = r"(?:ở|tại|đến|về|ghé|ra|vào|trong|trên|tới|khu|phòng)"
        pattern = rf'(?:{preps}\s+)?\b' + re.escape(substr) + r'\b'
        return re.sub(pattern, " ", text, flags=re.IGNORECASE).strip()

    def _remove_time_patterns(self, text: str) -> str:
        """Xóa các pattern chỉ thời gian từ text."""
        unit_pattern = r"(?:giờ|h|g|:)" 

        patterns = [
            rf"\b(?:vào|lúc|vào lúc)\s+\d{{1,2}}\s*{unit_pattern}\s*\d{{0,2}}(?:\s*(?:sáng|trưa|chiều|tối|đêm))?",
            r"\b(?:vào|lúc|vào lúc)?\s*\d{1,2}:\d{1,2}(?:\s*(?:sáng|trưa|chiều|tối|đêm))?",
            rf"\b(?:trước|sau|tầm|khoảng|từ|đến|kéo dài|trong)\s+\d{{1,2}}\s*{unit_pattern}\s*\d{{0,2}}(?:\s*(?:sáng|trưa|chiều|tối|đêm))?(?:\s*kém\s*\d+)?",
            rf"\d{{1,2}}\s*{unit_pattern}\s*\d{{0,2}}(?:\s*(?:sáng|trưa|chiều|tối|đêm))?(?:\s*kém\s*\d+)?(?:\s*rưỡi)?",
            r"\bkém\s*\d+(?:\s*(?:phút|p))?",
            r"\b(?:hôm nay|bữa nay|ngày mai|sáng mai|chiều mai|tối mai|mốt|kia|hôm qua)\b",
            r"\b(?:tuần sau|tháng sau|năm sau)\b",
            r"(?<!buổi\s)\b(?:sáng|trưa|chiều|tối|đêm)\b",
            r"(?<!buổi\s)\b(?:mai|nay)\b",
            r"\b(?:thứ)\s+(?:\d+|hai|ba|tư|năm|sáu|bảy)\b",
            r"\b(?:chủ nhật|cn)\b",
            r"\b(?:nãy giờ|tới giờ|ban nãy|lát nữa|sắp tới)\b",
            r"\bbuổi\s+(?:sáng|trưa|chiều|tối|đêm)\b",
            r"\b\d+\s*(?:tiếng|phút|p|h|giờ)\b",
            r"(?:nhắc|báo|gọi|alarm|nhac|bao)\s*(?:tôi|mình|me)?\s*(?:trước|sớm|lại|truoc|som|\s)*\d+(?:\.\d+)?\s*(?:phút|p|ph|tiếng|giờ|h|g)",
            r"(?:sau|trong|khoảng)\s+\d+(?:\s*(?:phút|giờ|tiếng))+\s+(?:nữa)?\s*(?:nhắc|báo|gọi|alarm|nhac|bao)?"
        ]
        
        cleaned_text = text
        for pat in patterns:
            cleaned_text = re.sub(pat, " ", cleaned_text, flags=re.IGNORECASE)
        return cleaned_text.strip()

    def _remove_habit_patterns(self, text: str, habit_info: dict) -> str:
        """Xóa các từ khóa thói quen (Bao gồm cả lỗi chính tả 'mõi')."""
        
        # Regex cho từ bắt đầu: mỗi, mõi, mọi, hàng, moi
        start_words = r"(?:mỗi|mõi|moi|hàng|mọi)"
        
        patterns = [
            # Bắt: mỗi ngày, mõi ngày, hàng tuần, mọi tháng...
            rf"\b{start_words}\s+(?:ngày|tuần|tháng|năm|sáng|trưa|chiều|tối|đêm|thứ\s*\d+|chủ nhật)\b",
            # Bắt: mỗi t2, hàng t3...
            rf"\b{start_words}\s+(?:t2|t3|t4|t5|t6|t7|cn)\b"
        ]
        
        cleaned_text = text
        for pat in patterns:
            cleaned_text = re.sub(pat, " ", cleaned_text, flags=re.IGNORECASE)
        return cleaned_text.strip()

    def _clean_event_name(self, text: str) -> str:
        """Dọn dẹp tên sự kiện."""
        # Xóa ký tự đặc biệt
        text = re.sub(r'[.,;!?]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        words = text.split()
        if not words: return ""
        while words:
            w = words[0].lower()
            if w in self.trash_words:
                words.pop(0)
            else:
                break
        
        # Xóa rác cuối câu
        while words and words[-1].lower() in self.trash_words:
            words.pop()
            
        return " ".join(words)

    def extract_event_name(self, raw_text: str, location: Optional[str], habit_info: dict) -> str:
        """Trích xuất tên sự kiện từ text GỐC."""
        current_text = raw_text
        
        # 1. Xóa địa điểm (Nếu có)
        if location:
            current_text = self._remove_substring(current_text, location)
            
        # 2. Xóa thói quen
        current_text = self._remove_habit_patterns(current_text, habit_info)
            
        # 3. Xóa thời gian
        current_text = self._remove_time_patterns(current_text)
        
        # 4. Clean rác và trả về
        result = self._clean_event_name(current_text)
        
        if result:
            return result[0].upper() + result[1:]
        return "Sự kiện mới"

    def _format_display_data(self, time_data: dict, location: str, habit_info: dict) -> dict:
        """Format dữ liệu hiển thị chuẩn cho Test Case (dd/mm/yyyy)."""
        date_str = "---"
        if time_data.get("date"):
            date_str = time_data["date"].strftime("%d/%m/%Y") 

        start_str = "---"
        if time_data.get("start_time"):
            h = time_data["start_time"]["hour"]
            m = time_data["start_time"]["minute"]
            start_str = f"{h:02}:{m:02}"

        end_str = "---"
        if time_data.get("end_time"):
            h = time_data["end_time"]["hour"]
            m = time_data["end_time"]["minute"]
            end_str = f"{h:02}:{m:02}"

        dur_str = "---"
        if time_data.get("duration"):
            total = int(time_data["duration"].total_seconds())
            h = total // 3600
            m = (total % 3600) // 60
            if m > 0:
                dur_str = f"{h}h{m}p" if h > 0 else f"{m}p"
            else:
                dur_str = f"{h}h"

        rem_str = "---"
        rem_min = time_data.get("reminder_minutes")
        if rem_min is not None:
            rem_str = f"{rem_min} phút"

        habit_str = "---"
        if habit_info.get("is_habit"):
            habit_str = habit_info.get("frequency", "daily").upper()

        return {
            "date": date_str,
            "start": start_str,
            "end": end_str,
            "duration": dur_str,
            "reminder": rem_str,
            "habit": habit_str,
            "location": location if location else "---"
        }
    def _restore_case(self, raw_text: str, clean_substr: str) -> str:
        """Khôi phục chữ hoa/thường từ chuỗi gốc."""
        if not clean_substr or not raw_text:
            return clean_substr

        match = re.search(re.escape(clean_substr), raw_text, re.IGNORECASE)
        if match:
            return match.group(0)
        return clean_substr.title()
    def process_command(self, raw_text: str) -> Dict[str, Any]:
        """Xử lý câu lệnh qua toàn bộ pipeline NLP."""
        if not raw_text or not isinstance(raw_text, str): return self._error_response()
        raw_text = raw_text.strip()
        if not raw_text: return self._error_response()

        # B1: Chuẩn hóa sơ bộ
        clean_text = self.preprocessor.process(raw_text)
        clean_text_lite = self.preprocessor.process_lite(raw_text)
        
        # B2: Phân tích thói quen
        habit_info = self.habit_parser.parse(clean_text)
        
        location_raw = self.location_parser.extract(raw_text)
        
        # B4: Trích xuất thời gian
        time_data = self.time_parser.parse(clean_text_lite)
        
        event_name = self.extract_event_name(raw_text, location_raw, habit_info)
        
        # Logic fallback: Nếu xóa sạch quá hóa ra rỗng, thử lại với clean_text
        if not event_name or event_name == "Sự kiện mới":
             event_temp = self.extract_event_name(clean_text, location_raw, habit_info)
             if event_temp and event_temp != "Sự kiện mới":
                 event_name = event_temp.capitalize()

        intent = "create_habit" if habit_info['is_habit'] else "create_event"
        
        # Format dữ liệu hiển thị (ưu tiên lấy chữ hoa từ raw text nếu có thể)
        final_location = location_raw
        if location_raw:
             # Đảm bảo hiển thị đúng case từ input gốc
             final_location = self._restore_case(raw_text, location_raw)

        display_data = self._format_display_data(time_data, final_location, habit_info)
        
        return {
            "intent": intent,
            "processed_text": clean_text,
            "data": {
                "event_name": event_name,
                "location": final_location,
                "time": time_data, 
                "habit_frequency": habit_info['frequency'],
                "reminder_minutes": time_data.get('reminder_minutes')
            },
            "display_data": display_data
        }

    @staticmethod
    def _error_response() -> Dict[str, Any]:
        return {
            "intent": "unknown",
            "processed_text": "",
            "data": { "event_name": "Sự kiện mới", "location": None, "time": {}, "habit_frequency": None, "reminder_minutes": None },
            "display_data": {}
        }
    @staticmethod
    def _remove_diacritics(text: str) -> str:
        if not text:
            return ""
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')

    @staticmethod
    def _date_key(time_obj: Any) -> str:
        if not time_obj:
            return "unknown"
        d = time_obj.get("date")
        try:
            return d.strftime("%Y-%m-%d")
        except Exception:
            return "unknown"

    @staticmethod
    def _loc_key(loc: Optional[str]) -> str:
        if not loc:
            return "unknown"
        s = NLPEngine._remove_diacritics(loc.lower())
        s = re.sub(r'[^\w\s]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s or "unknown"

    @staticmethod
    def _token_overlap(a: List[str], b: List[str]) -> float:
        if not a or not b:
            return 0.0
        sa, sb = set(a), set(b)
        return len(sa & sb) / max(len(sa), len(sb)) if max(len(sa), len(sb)) > 0 else 0.0

    def group_events(self, parsed_results: List[Dict[str, Any]], name_threshold: float = 0.5) -> List[Dict[str, Any]]:
        buckets = []
        for res in parsed_results:
            data = res.get("data", {})
            name = data.get("event_name") or ""
            loc = data.get("location")
            time_obj = data.get("time") or {}
            
            date_k = self._date_key(time_obj)
            loc_k = self._loc_key(loc)
            name_tokens = [t for t in name.split() if t and len(t) > 1]

            placed = False
            for b in buckets:
                if b["date_key"] != date_k: continue
                if b["loc_key"] != "unknown" and loc_k != "unknown" and b["loc_key"] != loc_k: continue
                
                overlap = self._token_overlap(name_tokens, b["name_tokens"])
                if overlap >= name_threshold:
                    b["members"].append(res)
                    b["name_tokens"] = list(set(b["name_tokens"]) | set(name_tokens))
                    rem = (time_obj.get("reminder_minutes") if isinstance(time_obj, dict) else None)
                    if rem is not None:
                        if b.get("reminder_minutes") is None:
                            b["reminder_minutes"] = rem
                        else:
                            b["reminder_minutes"] = min(b["reminder_minutes"], rem)
                    placed = True
                    break

            if not placed:
                buckets.append({
                    "name_tokens": name_tokens,
                    "date_key": date_k,
                    "loc_key": loc_k,
                    "members": [res],
                    "reminder_minutes": (time_obj.get("reminder_minutes") if isinstance(time_obj, dict) else None)
                })

        groups = []
        for i, b in enumerate(buckets, 1):
            first_member = b["members"][0]
            rep_name = first_member["data"]["event_name"]
            rep_loc = None if b["loc_key"] == "unknown" else first_member["data"]["location"]
            groups.append({
                "group_id": i,
                "representative_name": rep_name,
                "date": b["date_key"],
                "location": rep_loc,
                "count": len(b["members"]),
                "members": b["members"],
                "reminder_minutes": b.get("reminder_minutes")
            })
        return groups


if __name__ == "__main__":
    engine = NLPEngine()
    # Test case khó
    texts = [
        "Đi siêu thị BigC vào lúc 9 giờ tối nay",
        "Họp lúc 9h sáng",
        "Đi Đà Lạt",
        "Nhắc tôi đi họp nhóm",
        "Code python lúc 2h chiều",
        "Chủ nhật đi nhà thờ    "   ,
        "đi bộ buổi sáng mõi ngày "     ,
        "đá banh vào ngày mai lúc 6h10 tối tại sân huỳnh đức",
        "đi bơi ở hồ bơi lam sơn vào lúc 7 giờ tối thứ 7 tuần sau",
        " Về thăm nhà mỗi tháng   "
    ]
    
    print("-" * 60)
    for t in texts:
        res = engine.process_command(t)
        print(f"Input: {t}")
        print(f"Event: '{res['data']['event_name']}'")
        print(f"Loc:   {res['data']['location']}")
        print(f"Time:  {res['display_data']['start']}")
        print("-" * 60)
    