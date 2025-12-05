import json
import os
import re
from typing import List, Optional, Set


class LocationParser:
    """Trích xuất địa điểm từ câu tiếng Việt."""
    
    def __init__(self):
        self.locations_db = self._load_locations()
        
        self.stop_verbs: Set[str] = {
            "mua", "bán", "thuê", "ăn", "uống", "chơi", "ngủ", "nghỉ",
            "tắm", "vệ", "làm", "kiếm", "quẩy", "đi", "đá", "tập",
            "xem", "sửa", "khám", "chữa", "tuyển", "thăm", "đón", "rước",
            "gặp", "chờ", "đợi", "lấy", "nộp", "đông", "giảm", "hóng",
            "rút", "kẹt", "thi", "lội", "check", "coi", "nhìn", "thấy",
            "chụp", "quá", "tải", "lắm", "như", "tránh", "chạy", "hát",
            "hò", "đánh", "tìm", "cất", "la", "mắng", "chửi", "vào", "ra",
            "lên", "xuống", "biết", "hiểu", "dám", "thèm", "ưa", "ngán",
            "nhớ", "quên", "gửi", "bơi", "giữ",
        }
        
        self.black_list: Set[str] = {
            "ngủ thôi", "chơi nhé", "nghỉ ngơi", "vệ sinh", "làm việc",
            "học bài", "tắm rửa", "kiếm tiền", "đâu đó", "đâu", "nhé",
            "nha", "thôi", "luôn", "rồi", "ngay", "mạng", "lòng", "vẻ",
            "đồ", "mơ", "việc", "chuyện", "người", "lên mạng", "trong lòng",
            "ra vẻ", "lên đồ", "trong mơ", "vào việc", "ta đây",
            "người hâm mộ", "qua loa", "bộ", "buổi", "sáng", "trưa",
            "chiều", "tối", "đêm", "khuya", "hôm nay", "ngày mai", "mốt",
            "tuần", "tháng", "năm", "thứ 2", "thứ 3", "thứ 4", "thứ 5",
            "thứ 6", "thứ 7", "chủ nhật", "cn",
            
        }
        
        self.prep_pattern = re.compile(
            r"(?:tại|ở|đến|về|ghé|ra|trong|trên|tới|lên|xuống|vào)",
            re.IGNORECASE
        )
        
        noun_list = [
            "trung tâm thương mại", "khu vui chơi", "bãi giữ xe", "bãi gửi xe",
            "bệnh viện", "công viên", "chung cư", "siêu thị", "địa chỉ",
            "căn hộ", "thị xã", "trường", "phòng", "quán", "nhà", "chợ",
            "tiệm", "shop", "quận", "huyện", "thôn", "xóm", "hồ bơi", "hồ",
            "bãi", "khu", "số", "ngõ", "hẻm", "đường", "rạp", "phố",
            "sân", "nhà hàng", "cửa hàng", "quảng trường", "chung cư", "tòa nhà"
        ]
        self.noun_pattern = re.compile(
            r"(?:" + "|".join(noun_list) + r")",
            re.IGNORECASE
        )
        
        self.time_cut_markers = [
            " lúc ", " vào ", " trong ", " ngày ", " hôm ", " sáng ", " trưa ",
            " chiều ", " tối ", " mai ", " mốt ", " tuần ", " tháng ", " năm ",
            " thứ ", " cn "," mỗi ", " mọi ", " hằng "
        ]
    
    def _load_locations(self) -> List[str]:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "locations.json")
        
        if not os.path.exists(data_path):
            return []
        
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                locations = [loc for group in data.values() for loc in group]
                return sorted(locations, key=len, reverse=True)
        except Exception:
            return []
    
    def _is_invalid(self, text: str) -> bool:
        text = text.lower().strip()
        
        if re.search(r'\d+\s*(?:h|g|:|p|phút|giây|tiếng|am|pm)\b', text):
            return True
        
        if re.search(r'(?:ngày|tháng|năm|thứ)\s*\d+', text):
            return True
        
        time_words = [
            "hôm nay", "ngày mai", "mốt", "tuần", "tháng", "năm", "sáng",
            "trưa", "chiều", "tối", "đêm", "khuya", "thứ", "chủ nhật", "cn"
        ]
        if any(re.search(r'\b' + re.escape(w) + r'\b', text) for w in time_words):
            return True
        
        if len(text) < 2 or text.isdigit():
            return True
        
        if any(re.search(r'\b' + re.escape(b) + r'\b', text) for b in self.black_list):
            return True
        
        return False
    
    def _cut_time_tail(self, text: str) -> str:
        lower = " " + text.lower() + " "
        cut_pos = min(
            (lower.find(mark) for mark in self.time_cut_markers if lower.find(mark) != -1),
            default=None
        )
        return text[:cut_pos].strip() if cut_pos is not None else text
    
    def _clean_extracted_text(self, text: str) -> str:
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            lower = word.lower()
            prev = words[i - 1].lower() if i > 0 else ""
            
            if lower in self.stop_verbs or lower in ["phim", "ảnh", "hình"]:
                allow = False
                
                valid_pairs = {
                    ("bãi", "gửi"), ("bãi", "giữ"), ("hồ", "bơi"),
                    ("vui", "chơi"), ("phòng", "tập"), ("sân", "tập"),
                    ("trung tâm", "tập"), ("khu", "tập"), ("sân", "đá"),
                    ("bãi", "đá"), ("rạp", "phim"), ("coi", "phim"),
                    ("xem", "phim"), ("chụp", "ảnh"), ("studio", "ảnh"),
                    ("chụp", "hình"), ("studio", "hình"), ("thể", "hình"),
                    ("truyền", "hình"), ("màn", "hình"),
                    ("quán", "ăn"), ("nhà", "hàng"), ("sân", "bóng"), 
                    ("sân", "vận"), ("sân", "bay"), ("sân", "khấu"),
                    ("cửa", "hàng"), ("điểm", "hẹn"), ("nơi", "ở")
                }
                
                if (prev, lower) in valid_pairs:
                    allow = True
                
                if word[0].isupper() and i > 0:
                    allow = True
                
                if not allow:
                    break
            
            result.append(word)
        
        return " ".join(result).strip()
    
    def _post_process_clean(self, text: str) -> str:
        patterns = [
            r'^(địa chỉ|vị trí|nơi|nhà|quê)\s+(là|của|nằm|tại|ở)\s+',
            r'^(là|của|nằm|tại|ở)\s+',
            r'^(cái|ngôi|chiếc)\s+'
        ]
        for p in patterns:
            text = re.sub(p, '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def extract(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        candidates = []
        
        for place in self.locations_db:
            if re.search(r'\b' + re.escape(place) + r'\b', text_lower):
                candidates.append(place)
        time_stoppers = r"(?:\s+(?:lúc|vào|ngày|hôm|sáng|trưa|chiều|tối|đêm|mai|mốt|mỗi|hàng|mọi|hằng)|$|[.,?!])"
        candidates += re.findall(f"{self.prep_pattern.pattern}\s+(.*?){time_stoppers}", text, re.IGNORECASE)
        candidates += re.findall(f"(?:^|\s)({self.noun_pattern.pattern}\s+.*?){time_stoppers}", text, re.IGNORECASE)
        valid = []
        for raw in candidates:
            loc = self._cut_time_tail(raw)
            loc = self._clean_extracted_text(loc)
            loc = self._post_process_clean(loc)
            loc = loc.strip(" .,?!")
            
            if loc and not self._is_invalid(loc):
                valid.append(loc)
        
        return max(valid, key=len) if valid else None


if __name__ == "__main__":
    parser = LocationParser()
    print("\n🚀 LOCATION PARSER TEST\n")
    
    test_cases = [
        "thuê nhà ở ngõ 123 phố Huế",
        "tập gym ở phòng tập thể hình",
        "đi siêu thị lúc 9 giờ tối",
        "ghé 539/2/9 bình thới",
        "Đi bơi ở hồ bơi lam sơn",
        "Gửi xe ở bãi giữ xe rạp phim",
        "ăn uống tại quán phở 24/7",
        "học bài ở nhà bạn",
        "làm việc ở công ty ABC",
        "tắm rửa ở nhà",
        "đi chơi ở công viên 9/10",
        "đi khám bệnh viện đa khoa",
        "đi đá bóng ở sân tập thể thao",
        "đi xem phim ở rạp chiếu bóng",
        "Sáng mai 8h đưa con đi học ở trường tiểu học",
        "Đá banh vào ngày tại sân huỳnh đức"
        ""
    ]
    
    print(f"{'INPUT':<45} | {'OUTPUT'}")
    print("-" * 80)
    for t in test_cases:
        print(f"{t:<45} | {parser.extract(t)}")