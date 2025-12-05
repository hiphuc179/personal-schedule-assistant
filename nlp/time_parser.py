from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re


class TimeParser:
    """Parser xử lý thời gian từ câu tiếng Việt tự nhiên."""
    
    def __init__(self):
        self.num_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12
        }
        
        self.weekday_map = {
            "thứ hai": 0, "thứ 2": 0, "t2": 0, "thứ ba": 1, "thứ 3": 1, "t3": 1,
            "thứ tư": 2, "thứ 4": 2, "t4": 2, "thứ năm": 3, "thứ 5": 3, "t5": 3,
            "thứ sáu": 4, "thứ 6": 4, "t6": 4, "thứ bảy": 5, "thứ 7": 5, "t7": 5,
            "chủ nhật": 6, "cn": 6
        }
    
    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = self._normalize_half_past(text)
        text = self._normalize_kem(text)
        text = self._normalize_ruoi(text)
        text = self._normalize_ish(text)
        return text
    
    def _normalize_half_past(self, text: str) -> str:
        if "half past" not in text:
            return text
        for word, num in self.num_map.items():
            if word in text:
                return text.replace(f"half past {word}", f"{num}:30")
        return text
    
    def _normalize_kem(self, text: str) -> str:
        match = re.search(r'(\d{1,2})\s*(?:giờ|h|g)?\s*kém\s*(\d{1,2})', text)
        if not match:
            return text
        h = int(match.group(1))
        m_kem = int(match.group(2))
        target_h = h - 1 if h > 0 else 23
        target_m = 60 - m_kem
        return text.replace(match.group(0), f"{target_h}:{target_m}")
    
    def _normalize_ruoi(self, text: str) -> str:
        text = re.sub(r'(\d+)\s*tiếng\s*rưỡi', r'\1.5 tiếng', text)
        text = re.sub(r'(\d+)\s*(?:giờ|h|g)?\s*rưỡi', r'\1:30', text)
        return text
    
    def _normalize_ish(self, text: str) -> str:
        return re.sub(r'(\d+)-?ish', r'\1:00', text)
    
    def _parse_time_str(self, time_str: str, context_text: str = "") -> dict:
        match = re.search(r'(\d{1,2})\s*(?::|h|g|giờ)\s*(\d{1,2})?', time_str)
        
        if not match:
            if "lúc" in context_text or "vào" in context_text or ":" in time_str:
                match = re.search(r'(\d{1,2})', time_str)
                if match:
                    return self._adjust_am_pm(int(match.group(1)), 0, context_text)
            return None
        
        h = int(match.group(1))
        m = int(match.group(2)) if match.group(2) else 0
        return self._adjust_am_pm(h, m, context_text)
    
    def _adjust_am_pm(self, h: int, m: int, text: str) -> dict:
        text = text.lower()
        
        if ("chiều" in text or "tối" in text or "pm" in text) and h < 12:
            h += 12
        
        if ("sáng" in text or "am" in text) and h == 12:
            h = 0
        
        if 0 <= h <= 23 and 0 <= m <= 59:
            return {'hour': h, 'minute': m}
        return None
    
    def _parse_duration_str(self, text: str) -> timedelta:
        hours = minutes = 0
        found = False
        
        for match in re.finditer(r'(\d+(?:\.\d+)?)\s+(tiếng|giờ|h|g|phút|p|ph)\b', text):
            val = float(match.group(1))
            unit = match.group(2)
            
            if self._is_reminder_context(text, match):
                continue
            
            if unit in ['phút', 'p', 'ph']:
                minutes += int(val)
                found = True
            elif unit in ['tiếng']:
                hours += int(val)
                minutes += int((val - int(val)) * 60)
                found = True
            elif unit in ['giờ', 'h', 'g']:
                if self._is_duration_context(text, match):
                    hours += int(val)
                    minutes += int((val - int(val)) * 60)
                    found = True
        
        return timedelta(hours=hours, minutes=minutes) if found else None
    
    def _is_reminder_context(self, text: str, match) -> bool:
        start_idx = max(0, match.start() - 30)
        end_idx = min(len(text), match.end() + 30)
        
        pre_text = text[start_idx:match.start()]
        post_text = text[match.end():end_idx]
        full_context = text[start_idx:end_idx]
        
        if re.search(r'\b(?:nhắc|báo|gọi|alarm|nhac|bao)\b', pre_text, re.IGNORECASE):
            return True
        
        if re.search(r'\b(?:nhắc|báo|gọi|alarm|nhac|bao)\b', post_text, re.IGNORECASE):
            return True
        
        if re.search(
            r'(?:sau|trong|khoảng)\s+\d+(?:\s*(?:phút|giờ|tiếng))+\s+(?:nữa)?\s*(?:nhắc|báo|gọi|alarm|nhac|bao)',
            full_context, re.IGNORECASE
        ):
            return True
        
        return False
    
    def _is_duration_context(self, text: str, match) -> bool:
        start_idx = max(0, match.start() - 30)
        pre_text = text[start_idx:match.start()]
        post_text = text[match.end():match.end() + 20]
        
        if any(x in pre_text for x in ['trong', 'khoảng', 'tầm', 'mất', 'dài', 'chừng', 'kéo dài']):
            return True
        
        if "chiều" not in post_text and "sáng" not in post_text and "tối" not in post_text:
            return True
        
        return False
    
    def _extract_reminder(self, text: str) -> int:
        patterns = [
            r"\b(?:nhắc|báo|gọi|alarm|nhac|bao)(?:\s+(?:tôi|mình|me))?\s+(?:trước|sớm|sau|lại|truoc|som|lai)\s+(\d+(?:\.\d+)?)\s*(phút|p|ph|tiếng|giờ|h|g)",
            r"\b(?:nhắc|báo|gọi|alarm|nhac|bao).*?(?:sau|trong|khoảng)\s+(\d+(?:\.\d+)?)\s*(phút|p|ph|tiếng|giờ|h|g)\s+(?:nữa)?",
            r"(?:sau|trong|khoảng)\s+(\d+(?:\.\d+)?)\s*(phút|p|ph|tiếng|giờ|h|g)\s+(?:nữa)?\s*(?:nhắc|báo|gọi|alarm|nhac|bao)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._extract_reminder_value(match, text)
        
        return None
    
    def _extract_reminder_value(self, match, text: str) -> int:
        val = float(match.group(1))
        unit = match.group(2).lower()
        
        if unit in ['giờ', 'h', 'g', 'tiếng']:
            if re.search(r'\b(?:trước|sớm|sau|lại|truoc|som|lai)\b', match.group(0), re.IGNORECASE):
                return int(val * 60)
            return None
        
        if unit in ['phút', 'p', 'ph']:
            return int(val)
        
        return int(val * 60)
    
    def extract_date(self, text: str) -> datetime:
        text = text.lower()
        today = datetime.now()
        weekday_date = self._extract_weekday_date(text, today)
        if weekday_date:
            return weekday_date

        relative_date = self._extract_relative_date(text, today)
        if relative_date:
            return relative_date
        
        return today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _extract_relative_date(self, text: str, today: datetime) -> datetime:
        mapping = {
            r'hôm nay|bữa nay': 0,
            r'ngày mai|sáng mai|chiều mai|tối mai|mai\s': 1,
            r'mốt|ngày kia': 2,
            r'hôm qua': -1,
            r'tuần sau|tuần tới': 'weeks:1',
            r'tháng sau': 'months:1',
            r'năm sau': 'years:1',
        }
        
        for pattern, offset in mapping.items():
            if re.search(pattern, text):
                if isinstance(offset, int):
                    return (today + timedelta(days=offset)).replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    unit, value = offset.split(':')
                    value = int(value)
                    if unit == 'weeks':
                        return (today + timedelta(weeks=value)).replace(hour=0, minute=0, second=0, microsecond=0)
                    elif unit == 'months':
                        return (today + relativedelta(months=value)).replace(hour=0, minute=0, second=0, microsecond=0)
                    elif unit == 'years':
                        return (today + relativedelta(years=value)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return None
    
    def _extract_weekday_date(self, text: str, today: datetime) -> datetime:
        match = re.search(r'(thứ\s+(\w+|\d+)|chủ nhật|cn)', text)
        if not match:
            return None
        
        thu_str = match.group(1).replace("t2", "thứ 2").replace("t3", "thứ 3")
        
        for key, target_weekday in self.weekday_map.items():
            if key in thu_str:
                current_weekday = today.weekday()
                days_ahead = target_weekday - current_weekday
                
                if days_ahead <= 0:
                    days_ahead += 7
                
                if ("tuần sau" in text or "tuần tới" in text) and days_ahead <= 7:
                    days_ahead += 7
                
                result = today + timedelta(days=days_ahead)
                return result.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return None
    
    def parse(self, text: str) -> dict:
        original_text = text
        text = self._normalize_text(text)
        
        result = {
            "date": self.extract_date(original_text),
            "start_time": None,
            "end_time": None,
            "duration": None,
            "reminder_minutes": None
        }
        
        result["reminder_minutes"] = self._extract_reminder(text)
        
        range_result = self._parse_range_time(text, result["date"])
        if range_result:
            result.update(range_result)
            return result
        
        result["start_time"] = self._parse_start_time(text)
        if result["reminder_minutes"] is not None and result["start_time"] is None:
            now = datetime.now()
            result["start_time"] = {'hour': now.hour, 'minute': now.minute}
        
        text_for_duration = self._remove_start_time_from_text(text)
        result["duration"] = self._parse_duration_str(text_for_duration)
        
        if result["start_time"] and result["duration"]:
            dt_start = result["date"].replace(
                hour=result["start_time"]['hour'],
                minute=result["start_time"]['minute']
            )
            dt_end = dt_start + result["duration"]
            result["end_time"] = {'hour': dt_end.hour, 'minute': dt_end.minute}
        
        if result["start_time"] and not result["end_time"] and not result["duration"]:
            if re.search(r'(?:nãy giờ|tới giờ|đến giờ|tới nay|từ nãy)', text):
                now = datetime.now()
                dt_start = result["date"].replace(
                    hour=result["start_time"]['hour'],
                    minute=result["start_time"]['minute']
                )
                if dt_start > now:
                    dt_start -= timedelta(days=1)
                result["end_time"] = {'hour': now.hour, 'minute': now.minute}
                result["duration"] = now - dt_start
        
        return result
    
    def _parse_range_time(self, text: str, date: datetime) -> dict:
        match = re.search(
            r'(?:từ|bắt đầu)\s+(.*?)\s+(?:đến|tới|kết thúc lúc|xong lúc)\s+(.*)',
            text
        )
        
        if not match:
            return None
        
        t1 = self._parse_time_str(match.group(1), text)
        t2 = self._parse_time_str(match.group(2), text)
        
        if not (t1 and t2):
            return None
        
        dt1 = date.replace(hour=t1['hour'], minute=t1['minute'])
        dt2 = date.replace(hour=t2['hour'], minute=t2['minute'])
        
        if dt2 < dt1:
            dt2 += timedelta(days=1)
        
        return {
            "start_time": t1,
            "end_time": {'hour': dt2.hour, 'minute': dt2.minute},
            "duration": dt2 - dt1
        }
    
    def _parse_start_time(self, text: str) -> dict:
        match = re.search(
            r'(?:lúc|vào|từ|bắt đầu|kể từ)\s*(\d{1,2}(?::\d{2}|h|g| giờ)?(?:\s*\d{1,2})?)',
            text
        )
        
        if match:
            return self._parse_time_str(match.group(0), text)
        
        for match in re.finditer(r'(\d{1,2})(?::|h|g| giờ)\s*(\d{1,2})?', text):
            pre = text[max(0, match.start()-10):match.start()]
            
            if any(x in pre for x in ['trong', 'khoảng', 'mất', 'dài', 'trước', 'sớm', 'nhắc', 'báo']):
                continue
            
            return self._parse_time_str(match.group(0), text)
        
        return None
    
    def _remove_start_time_from_text(self, text: str) -> str:
        match = re.search(
            r'(?:lúc|vào|từ|bắt đầu|kể từ)\s*(\d{1,2}(?::\d{2}|h|g| giờ)?(?:\s*\d{1,2})?)',
            text
        )
        
        if match:
            return text[:match.start()] + " " + text[match.end():]
        
        return text


if __name__ == "__main__":
    parser = TimeParser()
    print("\n" + "="*115)
    print("🚀 KIỂM TRA LOGIC THỜI GIAN (TIME PARSER ONLY)")
    print(f"🕒 Thời gian hiện tại: {datetime.now().strftime('%H:%M %d/%m/%Y')}")
    print("="*115 + "\n")

    test_cases = [
        "hẹn lúc 9h sáng",
        "gặp nhau lúc 2h chiều",
        "tối nay 7g30 đi ăn",
        "đi ngủ lúc 23h",
        "gặp lúc 8h rưỡi sáng",
        "bây giờ là 10h kém 15",
        "học bài 2 tiếng rưỡi",
        "học từ 8h đến 10h",
        "làm việc từ 13h tới 17h30",
        "ca đêm từ 22h đến 6h sáng",
        "tôi làm nãy giờ từ 13h",
        "đợi từ 8h sáng tới giờ",
        "chạy bộ trong 30 phút",
        "họp kéo dài 2 tiếng",
        "sáng mai 8h đi cafe",
        "chiều mốt rảnh không",
        "thứ 2 tuần sau họp",
        "họp lúc 9h nhắc trước 15p",
        "báo sớm 30 phút đi đón con",
        "nhắc tôi uống thuốc lúc 20h",
        "Nhắc tôi uống thuốc sau 15 phút nữa",
        "Ngủ trưa lúc 12 giờ rưỡi",
       " Thứ 2 tuần sau nộp báo cáo  ",
       "Đi xem phim lúc 19:30    "  ,
       " Tối nay 7h đi chơi  ",
       " Sáng mai 9h đi họp  ",
       "Sáng mai 8h đưa con đi học ở trường tiểu h"
    ]

    print(f"{'INPUT':<40} | {'DATE':<10} | {'START':<6} | {'END':<6} | {'DUR':<8} | {'REMIND'}")
    print("-" * 115)
    
    for text in test_cases:
        try:
            res = parser.parse(text)
            
            d_str = res["date"].strftime("%d/%m") if res["date"] else "-"
            s_str = f"{res['start_time']['hour']:02}:{res['start_time']['minute']:02}" if res['start_time'] else "-"
            e_str = f"{res['end_time']['hour']:02}:{res['end_time']['minute']:02}" if res['end_time'] else "-"
            
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