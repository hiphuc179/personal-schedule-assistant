import json
import os
import re
import unicodedata

class LocationParser:
    def __init__(self):
        # 1. LOAD DỮ LIỆU
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "locations.json")
        
        self.locations_db = {}
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self.locations_db = json.load(f)
        
        # 2. STOP VERBS (Động từ cấm - Gặp là CẮT ĐUÔI)
        self.stop_verbs = [
            "mua", "bán", "thuê", "ăn", "uống", "chơi", "ngủ", "nghỉ", 
            "tắm", "vệ", "học", "làm", "kiếm", "quẩy", "đi", 
            "đá", "tập", "xem", "sửa", "khám", "chữa", "tuyển",
            "thăm", "đón", "rước", "gặp", "chờ", "đợi", "lấy", "nộp",
            "đông", "giảm", "hóng", "rút", "kẹt", "thi", "lội", "check",
            "chụp", "hình", "phim", "ảnh", "coi", "nhìn", "thấy",
            "quá", "tải", "lắm", "như", "là", "của",
            "tránh", "chạy", "hát", "hò", "đánh", "tìm", "cất",
            "la", "mắng", "chửi", "vào", "ra", "lên", "xuống",
            "biết", "hiểu", "dám", "thèm", "ưa", "ngán", "nhớ", "quên",
            "gửi", "bơi", "giữ" 
        ]
        
        # 3. BLACKLIST (Cụm từ rác)
        # 3. BLACKLIST (Cụm từ rác & ĐỊA ĐIỂM ẢO)
        # [UPDATE] Đã thêm: công tác, du lịch, tham quan...
       # 3. BLACKLIST (Cụm từ rác)
        self.black_list = [
            "ngủ thôi", "chơi nhé", "nghỉ ngơi", "vệ sinh",
            "làm việc", "học bài", "tắm rửa", "kiếm tiền", "đâu đó", 
            "đâu", "nhé", "nha", "thôi", "luôn", "rồi", "ngay",
            "mạng", "lòng", "vẻ", "đồ", "mơ", "việc", "chuyện", "người",
            "lên mạng", "trong lòng", "ra vẻ", "lên đồ", "trong mơ", "vào việc",
            "ta đây", "người hâm mộ", "qua loa",
            "công tác", "du lịch", "phượt", "tham quan", "dã ngoại",
            "bộ", "buổi" # <--- THÊM 'buổi' VÀO ĐÂY
        ]
        
    # --- HÀM 1: LỌC THỜI GIAN ---
    def _is_time_expression(self, text):
        text = text.lower().strip()
        if re.search(r'\d+\s*(h|g|:|p|phút|giây|tiếng|am|pm)', text): return True
        if re.search(r'(?:thứ\s+\d|thứ\s+hai|thứ\s+ba|chủ nhật|hôm\s+nay|ngày\s+mai|mốt|tuần)', text): return True
        if text in ["giờ", "phút", "giây", "hôm nay", "bây giờ", "lúc nãy", "ban nãy"]:
            return True
        if text.isdigit(): return True
        return False

    # --- HÀM 2: QUÉT TỪ ĐIỂN ---
    def _scan_dictionary(self, text):
        found = []
        all_places = []
        for key in self.locations_db:
            all_places.extend(self.locations_db[key])
        all_places.sort(key=len, reverse=True)
        
        for place in all_places:
            if re.search(r'\b' + re.escape(place) + r'\b', text, re.IGNORECASE):
                found.append(place)
        return found

    # --- HÀM 3: QUÉT REGEX & CẮT ĐUÔI ---
    def _scan_by_regex(self, text):
        # Từ khóa mở đầu
        prepositions = r"(?:tại|ở|đến|về|ghé|ra|trong|trên|tới|lên|xuống|vào)"
        # Danh từ địa điểm
        location_nouns = r"(?:khu vui chơi|trung tâm thương mại|bãi gửi xe|bãi giữ xe|hồ bơi|sân|quán|chợ|siêu thị|trường|công viên|nhà|bệnh viện|căn hộ|chung cư|tiệm|shop|trung tâm|hồ|bãi|khu|phòng)"
        
        # --- [FIX QUAN TRỌNG] TỪ KHÓA KẾT THÚC ---
        # Thêm: không, ko, chưa, bạn, anh, em, chị, nhỉ, hả, dấu hỏi...
        stop_list = r"buổi|lúc|vào|ngày|trong|hôm|sáng|trưa|chiều|tối|mai|mốt|kia|tuần|tháng|năm|cái|lận|nè|luôn|không|ko|chưa|bạn|anh|chị|em|nhỉ|hả|nhá|bộ|\?"
        
        found = []
        
        # Pattern A: Giới từ + Nội dung
        pat_prep = f"{prepositions}\s+(.*?)(?=\s(?:{stop_list})|$)"
        found.extend(re.findall(pat_prep, text, re.IGNORECASE))

        # Pattern B: Danh từ + Nội dung
        pat_noun = f"(?:^|\s)({location_nouns}\s*.*?)(?=\s(?:{stop_list})|$)"
        found.extend(re.findall(pat_noun, text, re.IGNORECASE))

        clean_found = []
        for loc in found:
            # Xóa dấu câu thừa ở cuối (VD: quận 9?)
            loc = loc.strip(" ?.!,")
            
            # 1. Lọc Time
            if self._is_time_expression(loc): continue

            words = loc.split()
            if not words: continue

            # 2. Check từ đầu tiên
            if words[0].lower() in self.stop_verbs: continue

            # 3. Cắt đuôi hành động
            valid_words = []
            for i, word in enumerate(words):
                w = word.lower()
                if w in self.stop_verbs:
                    # --- NGOẠI LỆ ---
                    prev = words[i-1].lower() if i > 0 else ""
                    if ((w == "gửi" or w == "giữ") and prev == "bãi"):
                        valid_words.append(word); continue
                    if (w == "bơi" and prev == "hồ"):
                        valid_words.append(word); continue
                    if (w == "chơi" and prev == "vui"):
                        valid_words.append(word); continue
                    break # CẮT
                valid_words.append(word)
            
            if not valid_words: continue
            final_loc = " ".join(valid_words).strip()
            
            if len(final_loc) < 2 or final_loc.isdigit(): continue
            if self._is_time_expression(final_loc): continue

            # 4. Check Blacklist
            is_blacklisted = False
            for bad_word in self.black_list:
                if re.search(r'\b' + re.escape(bad_word) + r'\b', final_loc.lower()):
                     is_blacklisted = True; break
            if is_blacklisted: continue

            # 5. Dọn rác
            final_loc = re.sub(r'^(nhà|quê)\s+(ở|tại)\s+', '', final_loc, flags=re.IGNORECASE)
            final_loc = re.sub(r'^(cái|ngôi|chiếc)\s+', '', final_loc, flags=re.IGNORECASE)
            
            clean_found.append(final_loc)
                
        return clean_found

    # --- HÀM 4: EXTRACT CHÍNH ---
    def extract(self, text):
        regex_locs = self._scan_by_regex(text)
        dict_locs = self._scan_dictionary(text)
        candidates = regex_locs + dict_locs
        return max(candidates, key=len) if candidates else None

# --- TEST ---
if __name__ == "__main__":
    parser = LocationParser()
    print("\n🚀 TEST FINAL V15...")
    test_cases = [
        "tối mai có việc đi quận 9 không bạn?", # -> quận 9 (Cắt 'không bạn?')
        "đi đâu đó chơi đi",                    # -> ---
        "căn hộ landmark 81",       
        "mỗi tuần đều đi bộ buổi sáng",
    ]
    for text in test_cases:
        loc = parser.extract(text)
        print(f"{text:<40} | {str(loc) if loc else '---'}")