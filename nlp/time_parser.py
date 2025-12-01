from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
import math

class TimeParser:
    def __init__(self):
        pass

    # ==========================================
    # GIAI ĐOẠN 1: CHUẨN HÓA TEXT
    # ==========================================
    def _normalize_text(self, text):
        text = text.lower()
        # 1. Half past
        if "half past" in text:
            map_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
            for word, num in map_num.items():
                if word in text:
                    text = text.replace(f"half past {word}", f"{num}:30")
                    break
        # 2. Xử lý "kém"
        match_kem = re.search(r'(\d{1,2})\s*(?:giờ|h|g)?\s*kém\s*(\d{1,2})', text)
        if match_kem:
            h = int(match_kem.group(1))
            m_kem = int(match_kem.group(2))
            target_h = h - 1 if h > 0 else 23
            target_m = 60 - m_kem
            text = text.replace(match_kem.group(0), f"{target_h}:{target_m}")
        # 3. Xử lý "rưỡi"
        text = re.sub(r'(\d+)\s*(?:tiếng|giờ)\s*rưỡi', r'\1.5 tiếng', text)
        text = re.sub(r'(\d+)\s*(?:giờ|h|g)\s*rưỡi', r'\1:30', text)
        # 4. Fuzzy words
        text = re.sub(r'(\d+)-?ish', r'\1:00', text)
        return text

    # ==========================================
    # HELPER PARSERS
    # ==========================================
    def _parse_time_str(self, time_str, context_text=""):
        # Bắt chuỗi giờ: 9h, 9:30, 9g
        match = re.search(r'(\d{1,2})\s*(?::|h|g|giờ)\s*(\d{1,2})?', time_str)
        if not match:
            # Fallback: Nếu có từ khóa lúc/vào thì bắt số trơ trọi (lúc 9)
            if "lúc" in context_text or "vào" in context_text or ":" in time_str:
                match = re.search(r'(\d{1,2})', time_str)
                if match: return self._adjust_am_pm(int(match.group(1)), 0, context_text)
            return None
        h = int(match.group(1))
        m = int(match.group(2)) if match.group(2) else 0
        return self._adjust_am_pm(h, m, context_text)

    def _adjust_am_pm(self, h, m, text):
        text = text.lower()
        # Logic 12h/24h
        if ("chiều" in text or "tối" in text or "pm" in text) and h < 12:
            h += 12
        if ("sáng" in text or "am" in text) and h == 12:
            h = 0
        if 0 <= h <= 23 and 0 <= m <= 59:
            return {'hour': h, 'minute': m}
        return None

    def _parse_duration_str(self, text):
        hours = 0
        minutes = 0
        found = False
        # Regex bắt duration
        matches = re.finditer(r'(\d+(?:\.\d+)?)\s*(tiếng|giờ|h|g|phút|p|ph)', text)
        
        for match in matches:
            val = float(match.group(1))
            unit = match.group(2)
            
            # [FIX QUAN TRỌNG] Check xem có phải là Reminder không?
            start_idx = max(0, match.start() - 15)
            pre_text = text[start_idx:match.start()]
            # Nếu thấy từ khóa nhắc nhở trước con số -> BỎ QUA (Để hàm _extract_reminder lo)
            if re.search(r'(trước|sớm|lại|nhắc|báo)\s*$', pre_text):
                continue

            if unit in ['phút', 'p', 'ph']:
                minutes += int(val); found = True
            elif unit in ['tiếng']:
                hours += int(val); minutes += int((val - int(val)) * 60); found = True
            else: # giờ, h, g
                # Check context để không bắt nhầm giờ (10h) thành duration
                if any(x in pre_text for x in ['trong', 'khoảng', 'tầm', 'mất', 'dài', 'chừng', 'kéo dài']):
                    hours += int(val); minutes += int((val - int(val)) * 60); found = True
                elif "chiều" not in text[match.end():] and "sáng" not in text[match.end():]:
                     hours += int(val); minutes += int((val - int(val)) * 60); found = True

        if found: return timedelta(hours=hours, minutes=minutes)
        return None

    # --- CẬP NHẬT HÀM NÀY TRONG time_parser.py ---
    def _extract_reminder(self, text):
        # Regex hỗ trợ cả có dấu và không dấu
        pattern = r"\b(?:nhắc|báo|gọi|alarm|nhac|bao)(?:\s+tôi|\s+mình| me)?\s*(?:trước|sớm|lại|truoc|som|\s)*(\d+(?:\.\d+)?)\s*(phút|p|ph|tiếng|giờ|h|g)"
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            unit = match.group(2).lower()
            if unit in ['phút', 'p', 'ph']: return int(val)
            else: return int(val * 60)
        return None

    # ==========================================
    # MAIN LOGIC
    # ==========================================
    def parse(self, text):
        original_text = text
        text = self._normalize_text(text)
        
        result = {
            "date": self.extract_date(original_text),
            "start_time": None,
            "end_time": None,
            "duration": None,
            "reminder_minutes": None
        }
        
        # 1. Bắt Reminder (Chạy trước để không bị Duration ăn mất)
        result["reminder_minutes"] = self._extract_reminder(text)

        # 2. Xử lý Range (Từ A đến B)
        match_range = re.search(r'(?:từ|bắt đầu)\s+(.*?)\s+(?:đến|tới|kết thúc lúc|xong lúc)\s+(.*)', text)
        if match_range:
            t1 = self._parse_time_str(match_range.group(1), text) 
            t2 = self._parse_time_str(match_range.group(2), text)
            if t1 and t2:
                result["start_time"] = t1
                dt1 = result["date"].replace(hour=t1['hour'], minute=t1['minute'])
                dt2 = result["date"].replace(hour=t2['hour'], minute=t2['minute'])
                if dt2 < dt1: dt2 += timedelta(days=1)
                result["end_time"] = {'hour': dt2.hour, 'minute': dt2.minute}
                result["duration"] = dt2 - dt1
                return result

        # 3. Tìm Start Time
        # Regex tìm giờ có từ khóa dẫn đường
        start_match = re.search(r'(?:lúc|vào|từ|bắt đầu|kể từ)\s*(\d{1,2}(?::\d{2}|h|g| giờ)?(?:\s*\d{1,2})?)', text)
        
        # Nếu không thấy, tìm giờ trơ trọi (nhưng phải check kỹ)
        if not start_match:
            potential_times = re.finditer(r'(\d{1,2})(?::|h|g| giờ)\s*(\d{1,2})?', text)
            for match in potential_times:
                pre = text[max(0, match.start()-10):match.start()]
                # Tránh bắt nhầm duration hoặc reminder
                if not any(x in pre for x in ['trong', 'khoảng', 'mất', 'dài', 'trước', 'sớm', 'nhắc', 'báo']):
                    start_match = match
                    break
        
        text_for_duration = text
        if start_match:
            result["start_time"] = self._parse_time_str(start_match.group(0), text)
            # Xóa giờ start khỏi text để tìm duration chính xác hơn
            text_for_duration = text[:start_match.start()] + " " + text[start_match.end():]

        # 4. Tìm Duration
        explicit_duration = self._extract_duration_from_segment(text_for_duration)
        if explicit_duration:
            result["duration"] = explicit_duration
            if result["start_time"]:
                dt_start = result["date"].replace(hour=result["start_time"]['hour'], minute=result["start_time"]['minute'])
                dt_end = dt_start + explicit_duration
                result["end_time"] = {'hour': dt_end.hour, 'minute': dt_end.minute}
        
        # 5. Logic "Nãy giờ"
        if result["start_time"] and not result["end_time"] and not result["duration"]:
            if re.search(r'(?:nãy giờ|tới giờ|đến giờ|tới nay|từ nãy)', text):
                now = datetime.now()
                dt_start = result["date"].replace(hour=result["start_time"]['hour'], minute=result["start_time"]['minute'])
                if dt_start > now: dt_start -= timedelta(days=1)
                result["end_time"] = {'hour': now.hour, 'minute': now.minute}
                result["duration"] = now - dt_start

        return result

    def _extract_duration_from_segment(self, text):
        return self._parse_duration_str(text)

    def extract_date(self, text):
        text = text.lower()
        today = datetime.now()
        target_date = today
        found = False
        
        if "hôm nay" in text or "bữa nay" in text: found = True
        elif "ngày mai" in text or "sáng mai" in text or "chiều mai" in text or "tối mai" in text or "mai " in text:
            target_date = today + timedelta(days=1); found = True
        elif "mốt" in text or "ngày kia" in text: target_date = today + timedelta(days=2); found = True
        elif "hôm qua" in text: target_date = today - timedelta(days=1); found = True
        elif "tuần sau" in text or "tuần tới" in text: target_date = today + timedelta(weeks=1); found = True
        elif "tháng sau" in text: target_date = today + relativedelta(months=1); found = True
        elif "năm sau" in text: target_date = today + relativedelta(years=1); found = True

        if not found:
            match_thu = re.search(r'(thứ\s+(\w+|\d+)|chủ nhật|cn)', text)
            if match_thu:
                weekday_map = {"thứ hai": 0, "thứ 2": 0, "thứ ba": 1, "thứ 3": 1, "thứ tư": 2, "thứ 4": 2, "thứ năm": 3, "thứ 5": 3, "thứ sáu": 4, "thứ 6": 4, "thứ bảy": 5, "thứ 7": 5, "chủ nhật": 6, "cn": 6}
                thu_str = match_thu.group(1).replace("t2", "thứ 2").replace("t3", "thứ 3")
                for key, val in weekday_map.items():
                    if key in thu_str:
                        target_weekday = val
                        current_weekday = today.weekday()
                        days_ahead = target_weekday - current_weekday
                        if days_ahead <= 0: days_ahead += 7
                        if ("tuần sau" in text or "tuần tới" in text) and days_ahead <= 7: days_ahead += 7
                        target_date = today + timedelta(days=days_ahead)
                        break
        return target_date.replace(hour=0, minute=0, second=0, microsecond=0)

if __name__ == "__main__":
    parser = TimeParser()
    print("\n" + "="*115)
    print("🚀 KIỂM TRA LOGIC THỜI GIAN (TIME PARSER ONLY)")
    print(f"🕒 Thời gian hiện tại (giả lập): {datetime.now().strftime('%H:%M %d/%m/%Y')}")
    print("="*115 + "\n")

    test_cases = [
        # --- NHÓM 1: GIỜ CƠ BẢN ---
        "hẹn lúc 9h sáng",                  # 09:00
        "gặp nhau lúc 2h chiều",            # 14:00 (Auto PM)
        "tối nay 7g30 đi ăn",               # 19:30
        "đi ngủ lúc 23h",                   # 23:00
        
        # --- NHÓM 2: CÁCH NÓI TỰ NHIÊN ---
        "gặp lúc 8h rưỡi sáng",             # 08:30
        "bây giờ là 10h kém 15",            # 09:45
        "học bài 2 tiếng rưỡi",             # Duration: 2h30m
        
        # --- NHÓM 3: KHOẢNG THỜI GIAN (RANGE) ---
        "học từ 8h đến 10h",                # Start: 08:00, End: 10:00
        "làm việc từ 13h tới 17h30",        # Start: 13:00, End: 17:30
        "ca đêm từ 22h đến 6h sáng",        # Start: 22:00, End: 06:00 (+1 ngày)
        
        # --- NHÓM 4: LOGIC "NÃY GIỜ" ---
        "tôi làm nãy giờ từ 13h",           # Start: 13:00, End: Now
        "đợi từ 8h sáng tới giờ",           # Start: 08:00, End: Now
        
        # --- NHÓM 5: THỜI LƯỢNG (DURATION) ---
        "chạy bộ trong 30 phút",            # Duration: 30m
        "họp kéo dài 2 tiếng",              # Duration: 2h
        
        # --- NHÓM 6: NGÀY THÁNG ---
        "sáng mai 8h đi cafe",              # Date: Now + 1
        "chiều mốt rảnh không",             # Date: Now + 2
        "thứ 2 tuần sau họp",               # Date: Thứ 2 kế tiếp
        
        # --- NHÓM 7: NHẮC NHỞ (REMINDER) - QUAN TRỌNG ---
        "họp lúc 9h nhắc trước 15p",        # Start: 09:00, Remind: 15
        "báo sớm 30 phút đi đón con",       # Remind: 30
        "nhắc tôi uống thuốc lúc 20h",      # Start: 20:00\
        "tôi làm bài từ 10h sáng tới giờ",
        "nãy giờ tôi làm việc cũng được 2 tiếng"
    ]

    print(f"{'INPUT':<40} | {'DATE':<10} | {'START':<6} | {'END':<6} | {'DUR':<8} | {'REMIND'}")
    print("-" * 115)
    
    for text in test_cases:
        try:
            res = parser.parse(text)
            
            # Format hiển thị
            d_str = res["date"].strftime("%d/%m") if res["date"] else "-"
            
            s_str = "-"
            if res['start_time']:
                s_str = f"{res['start_time']['hour']:02}:{res['start_time']['minute']:02}"
                
            e_str = "-"
            if res['end_time']:
                e_str = f"{res['end_time']['hour']:02}:{res['end_time']['minute']:02}"
                
            dur_str = "-"
            if res['duration']:
                total = int(res['duration'].total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                dur_str = f"{h}h{m}p"
            
            rem_str = f"{res['reminder_minutes']}p" if res['reminder_minutes'] is not None else "-"

            print(f"{text:<40} | {d_str:<10} | {s_str:<6} | {e_str:<6} | {dur_str:<8} | {rem_str}")
            
        except Exception as e:
            print(f"{text:<40} | ❌ LỖI: {e}")

    print("-" * 115)