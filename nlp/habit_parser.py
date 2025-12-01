import re

class HabitParser:
    def __init__(self):
        self.patterns = [
            # 1. Weekly (Ưu tiên cao nhất)
            ("weekly", r"(?:mỗi|hàng|mọi)\s*(?:tuần|thứ|chủ nhật|cn|t2|t3|t4|t5|t6|t7)"),
            # 2. Monthly
            ("monthly", r"(?:mỗi|hàng|mọi)\s+(?:tháng)"),
            # 3. Yearly
            ("yearly", r"(?:mỗi|hàng|mọi)\s+(?:năm)"),
            # 4. Daily (Ưu tiên thấp nhất - vì dễ bắt nhầm 'mỗi sáng')
            ("daily", r"(?:mỗi|hàng|mọi)\s+(?:ngày|sáng|trưa|chiều|tối|đêm)")
        ]

    def parse(self, text):
        """
        Input: "đi bơi mỗi chiều chủ nhật"
        Output: is_habit=True, frequency=weekly, remaining_text="đi bơi"
        """
        frequency = None
        clean_text = text
        
        for freq, pattern in self.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                frequency = freq
                # Xóa từ khóa habit khỏi câu
                clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE).strip()
                break 
                
        return {
            "is_habit": frequency is not None,
            "frequency": frequency,
            "remaining_text": clean_text
        }