import json
import os
import re
import unicodedata
try:
    from underthesea import word_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False
    print("⚠️ Cảnh báo: Chưa cài 'underthesea'. Đang chạy chế độ Rule-based thuần túy.")
class Preprocessor:
    def __init__(self):
        # Xác định đường dẫn file data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        
        # 1. LOAD TEENCODE (replace_dict.json)
        self.replace_dict = {}
        path_replace = os.path.join(data_dir, "replace_dict.json")
        if os.path.exists(path_replace):
            with open(path_replace, "r", encoding="utf-8") as f:
                self.replace_dict = json.load(f)
        
        # 2. LOAD ANH-VIỆT (en_vi.json)
        self.en_vi_dict = {}
        path_en_vi = os.path.join(data_dir, "en_vi.json")
        if os.path.exists(path_en_vi):
            with open(path_en_vi, "r", encoding="utf-8") as f:
                self.en_vi_dict = json.load(f)

        # 3. LOAD IGNORE WORDS (Cho có, chứ file này không dùng để xóa từ)
        self.ignore_words = []
        path_ignore = os.path.join(data_dir, "ignore_words.json")
        if os.path.exists(path_ignore):
            with open(path_ignore, "r", encoding="utf-8") as f:
                self.ignore_words = json.load(f)

    def _basic_normalize(self, text):
        if not text: return ""
        # Chuyển về chữ thường và chuẩn hóa Unicode
        return unicodedata.normalize("NFC", text.lower())
    def _nlp_segmentation(self, text):
        """
        [HYBRID] Sử dụng mô hình AI (Underthesea) để tách từ.
        VD: "thực hiện" -> "thực_hiện" (giúp máy hiểu là 1 từ)
        Tuy nhiên, để tương thích với Regex cũ, ta sẽ join lại bằng khoảng trắng.
        Mục đích chính: Chuẩn hóa khoảng cách giữa các từ.
        """
        if HAS_UNDERTHESEA:
            try:
                # word_tokenize trả về list: ['hôm_nay', 'tôi', 'đi', 'học']
                # Ta join lại và thay _ bằng khoảng trắng để khớp với Regex cũ
                tokens = word_tokenize(text)
                text = " ".join(tokens).replace("_", " ")
            except Exception:
                pass # Nếu lỗi model thì bỏ qua, dùng text gốc
        return text
    def _process_context_rules(self, text):
            """
            Xử lý ngữ cảnh thông minh cho từ đa nghĩa (VD: 'hn')
            """
            # 1. HN -> Hà Nội (nếu đứng sau giới từ chỉ địa điểm)
            # VD: ở hn, về hn, đến hn -> ở hà nội, về hà nội
            text = re.sub(r'\b(ở|tại|về|đến|ghé|ra|trong|đi|tới)\s+hn\b', r'\1 hà nội', text)
            
            # 2. HN -> Hôm nay (các trường hợp còn lại)
            # VD: hn tôi đi học -> hôm nay tôi đi học
            text = re.sub(r'\bhn\b', 'hôm nay', text)
            
            return text
    def _translate_en_vi(self, text):
        """Dịch Anh -> Việt"""
        if not self.en_vi_dict: return text
        
        # Sắp xếp từ dài lên trước
        sorted_keys = sorted(self.en_vi_dict.keys(), key=len, reverse=True)
        for key in sorted_keys:
            pattern = r'\b' + re.escape(key) + r'\b'
            text = re.sub(pattern, self.en_vi_dict[key], text)
        return text

    def _replace_phrases(self, text):
        """Dịch Teencode -> Việt"""
        if not self.replace_dict: return text
        
        sorted_keys = sorted(self.replace_dict.keys(), key=len, reverse=True)
        for key in sorted_keys:
            pattern = r'\b' + re.escape(key) + r'\b'
            text = re.sub(pattern, self.replace_dict[key], text)
        return text
    
    

    def process(self, text):
        # B1: Chuẩn hóa
        text = self._basic_normalize(text)
        
        # B2: Xử lý ngữ cảnh thông minh (CHẠY TRƯỚC TỪ ĐIỂN CỨNG)
        text = self._process_context_rules(text)
        
        # B3: Dịch Anh -> Việt
        text = self._translate_en_vi(text)
        
        # B4: Dịch Teencode còn lại
        text = self._replace_phrases(text)
        
        # B5: Dọn rác
        text = re.sub(r'\s+', ' ', text).strip()
        return text

# --- PHẦN TEST TỔNG HỢP (Copy đè vào cuối file nlp/preprocessor.py) ---
if __name__ == "__main__":
    p = Preprocessor()
    
    print("\n" + "="*80)
    print(f"🚀 TRẠNG THÁI HỆ THỐNG:")
    print(f"- Teencode loaded: {len(p.replace_dict)} từ")
    print(f"- En-Vi loaded:    {len(p.en_vi_dict)} từ")
    print(f"- Ignore loaded:   {len(p.ignore_words)} từ")
    print("="*80 + "\n")

    test_suite = {
        # --- NHÓM 1: KIỂM TRA NGỮ CẢNH "HN" (Hà Nội vs Hôm Nay) ---
        "TEST CONTEXT HN": [
            "hn tui đi công tác",               # hn đứng đầu -> hôm nay
            "tối hn rảnh ko",                   # hn đứng sau thời gian -> hôm nay
            "nhà t ở hn nha",                   # sau 'ở' -> hà nội
            "mai về hn ăn tết",                 # sau 'về' -> hà nội
            "ghé hn chơi xíu",                  # sau 'ghé' -> hà nội
            "hn mưa to ở hn",                   # Combo: hôm nay ... hà nội
            "tại hn đang kẹt xe",               # sau 'tại' -> hà nội
            "hn b đi đâu",                      # hôm nay
        ],
        
        # --- NHÓM 2: KIỂM TRA MƯA / MUA / TRÔI / TRỜI ---
        "TEST MƯA/MUA/TRÔI": [
            "hn đang mua to lắm",               # mua to -> mưa to
            "sg đang dang mua",                 # dang mua -> đang mưa
            "đi siêu thị mua đồ",               # mua đồ -> giữ nguyên (không đổi thành mưa)
            "mua 3kg táo",                      # mua -> giữ nguyên
            "thời gian troi qua mau",           # troi qua -> trôi qua
            "nắng quá tr quá đất",              # tr -> trời
        ],

        # --- NHÓM 3: ANH - VIỆT & CÔNG VIỆC ---
        "TEST ENGLISH": [
            "set cái meeting gấp",              # set -> thiết lập, meeting -> cuộc họp
            "boss confirm chưa",                # boss -> sếp, confirm -> xác nhận
            "deadline dí sấp mặt",              # deadline -> giữ nguyên
            "gửi file report cho manager",      # file giữ nguyên, manager -> quản lý
            "check mail dùm t",                 # mail giữ nguyên
            "m doc cuon book này chua",         # doc -> đọc, book -> sách, cuon -> cuốn
        ],

        # --- NHÓM 4: KHÔNG DẤU & TEENCODE KHÓ ---
        "TEST KHÔNG DẤU": [
            "hn toi Co ChUyen ConG TaC",        # toi->tôi, co->có, chuyen->chuyến, cong tac->công tác
            "r h 2 b s r da Vai S tRoi qua",    # vai s -> vài giây, troi qua -> trôi qua
            "lam viec met qua",                 # lam->làm, met->mệt (nếu có trong dict)
            "ko dc dau nha",                    # ko->không, dc->được
            "uhm thui ke di",                   # thui->thôi
        ],

        # --- NHÓM 5: ĐỊA ĐIỂM & HỖN HỢP ---
        "TEST MIX": [
            "đi vt cùng nhom",                  # vt->vũng tàu, nhom->nhóm
            "ghé dn ăn mì quảng",               # dn->đà nẵng
            "ra q7 ngắm cảnh",                  # q7->quận 7
            "tp hcm kẹt xe vch",                # tp hcm->thành phố hồ chí minh, vch->vãi chưởng
            "hẹn t2 tuần sau 9h sáng",          # t2->thứ hai, 9h giữ nguyên
            "cn này rảnh ko",                   # cn->chủ nhật
             "toi nay 7h ranh ko",
        ]
    }

    print(f"{'INPUT':<40} | {'OUTPUT (Kết quả xử lý)':<50}")
    print("-" * 95)
    
    for category, cases in test_suite.items():
        print(f"--- {category} ---")
        for text in cases:
            output = p.process(text)
            print(f"{text:<40} | {output}")
        print("-" * 95)