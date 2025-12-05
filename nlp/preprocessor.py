import json
import os
import re
import unicodedata
import json
from typing import Optional

try:
    from underthesea import word_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False


class Preprocessor:
    """Preprocessor: Chuẩn hóa, dịch và khôi phục dấu văn bản tiếng Việt."""

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")
        
        self.replace_dict = self._load_json("replace_dict.json")
        self.en_vi_dict = self._load_json("en_vi.json")
        self.ambiguity_dict = self._load_json("ambiguity.json")
        
    def _load_json(self, file_name: str) -> dict:
        """Tải từ điển JSON từ thư mục data."""
        path = os.path.join(self.data_dir, file_name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading {file_name}: {e}")
        return {}

    def _basic_normalize(self, text: str) -> str:
        """Chuẩn hóa: chuyển thường + NFC."""
        if not text:
            return ""
        return unicodedata.normalize("NFC", text.lower())

    def _remove_diacritics(self, text: str) -> str:
        """Loại bỏ dấu tiếng Việt để tương thích với parser."""
        if not text:
            return ""
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')

    def _apply_dict_translation(self, text: str, dictionary: dict) -> str:
        """Áp dụng dịch từ điển với so khớp ranh giới từ."""
        if not dictionary:
            return text
            
        sorted_keys = sorted(dictionary.keys(), key=len, reverse=True)
        for key in sorted_keys:
            pattern = r'(?<!\w)' + re.escape(key) + r'(?!\w)'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in reversed(matches):
                start, end = match.span()
                text = text[:start] + dictionary[key] + text[end:]
        
        return text
    
    def _segment_words(self, text: str) -> str:
        """Tách từ sử dụng underthesea nếu có sẵn."""
        if HAS_UNDERTHESEA:
            try:
                tokens = word_tokenize(text)
                return " ".join(tokens).replace("_", " ")
            except Exception:
                pass
        return text
    # Trong file preprocessor.py

    def process_lite(self, text: str) -> str:
        """[MỚI] Xử lý nhẹ: Chỉ sửa teencode/dấu, KHÔNG tách từ (để giữ format giờ 9:30)."""
        if not text:
            return ""

        text = self._basic_normalize(text)
        text = self._apply_dict_translation(text, self.ambiguity_dict)
        text = self._apply_dict_translation(text, self.en_vi_dict)
        text = self._apply_dict_translation(text, self.replace_dict)
        
        # [QUAN TRỌNG] KHÔNG GỌI self._segment_words(text) Ở ĐÂY
        
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    def process(self, text: str) -> str:
        """Pipeline: chuẩn hóa → nhập nhằng → anh-việt → teencode → tách từ."""
        if not text:
            return ""

        text = self._basic_normalize(text)
        text = self._apply_dict_translation(text, self.ambiguity_dict)
        text = self._apply_dict_translation(text, self.en_vi_dict)
        text = self._apply_dict_translation(text, self.replace_dict)
        text = self._segment_words(text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def process_for_parsers(self, text: str) -> str:
        """Xử lý văn bản không dấu dành cho các parser."""
        normalized = self.process(text)
        return self._remove_diacritics(normalized)

    def humanize(self, text: Optional[str]) -> Optional[str]:
        """Khôi phục dấu từ tất cả các từ điển."""
        if not text:
            return text
        
        text = self._apply_dict_translation(text, self.ambiguity_dict)
        text = self._apply_dict_translation(text, self.en_vi_dict)
        text = self._apply_dict_translation(text, self.replace_dict)
        
        return text


if __name__ == "__main__":
    p = Preprocessor()
    
    print("\n" + "="*120)
    print("🚀 TEST PREPROCESSOR")
    print("="*120 + "\n")

    test_cases = {
        "TEENCODE": [
            "Ko dC daU nHa",
            "tOi nAy di da banH vs B",
            "mK thich aN pHo",
        ],
        "CONTEXT": [
            "HN tui di an cuoi",
            "mai tui ve Hn an tet",
        ],
        "ENGLISH": [
            "Set cai Meeting gap",
            "Boss Confirm chua",
            "Call cho mk gap",
            "tôi làm bài từ nãy giờ cũng được 10 tiếng rồi",
            "đi bộ buổi sáng mõi ngày",
            "t2 tuan sau nop bao cao o phong 302",
            "Họp team online"
        ]
    }

    print(f"{'INPUT':<40} | {'PROCESS':<40} | {'HUMANIZE':<40}")
    print("-" * 125)
    
    for category, cases in test_cases.items():
        print(f"\n--- {category} ---")
        for text in cases:
            processed = p.process(text)
            humanized = p.humanize(processed)
            print(f"{text:<40} | {processed:<40} | {humanized:<40}")