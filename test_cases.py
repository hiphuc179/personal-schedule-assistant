import sys
import os
from datetime import datetime, timedelta

# Import NLPEngine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from nlp.nlp_engine import NLPEngine
except ImportError:
    print("❌ Lỗi: Không tìm thấy file nlp_engine.py. Hãy đảm bảo các file nằm cùng thư mục.")
    sys.exit(1)

# ==============================================================================
# UTILS: HÀM TÍNH NGÀY ĐỘNG (Dynamic Date) - Để test luôn đúng theo thời gian thực
# ==============================================================================
def get_date_str(offset_days=0):
    """Lấy ngày format dd/mm/yyyy."""
    d = datetime.now() + timedelta(days=offset_days)
    return d.strftime("%d/%m/%Y")

def get_weekday_date_str(weekday_idx, weeks_ahead=0):
    """Lấy ngày của thứ trong tuần (0=T2, 6=CN)."""
    today = datetime.now()
    current_weekday = today.weekday()
    days_ahead = weekday_idx - current_weekday
    if days_ahead <= 0: days_ahead += 7
    if weeks_ahead > 0 and days_ahead <= 7: days_ahead += 7
    target = today + timedelta(days=days_ahead)
    return target.strftime("%d/%m/%Y")

# ==============================================================================
# BỘ DỮ LIỆU TEST (55 CASES)
# ==============================================================================
# Cấu trúc: { "text": "...", "expect": { "event": "...", "time": "...", "loc": "...", ... } }
# Các trường expect: event, start, end, date, dur, loc, remind, habit
# Nếu không ghi expect trường nào, mặc định là "---" hoặc "-"

TEST_CASES = [
    # --- NHÓM 1: CÂU LỆNH CƠ BẢN (Không thời gian/địa điểm) ---
    {"text": "Đi ngủ", "expect": {"event": "Đi ngủ", "date": get_date_str(0)}},
    {"text": "Ăn cơm", "expect": {"event": "Ăn cơm", "date": get_date_str(0)}},
    {"text": "Chạy bộ", "expect": {"event": "Chạy bộ"}},
    {"text": "Họp team", "expect": {"event": "Họp team"}},
    {"text": "Gọi điện cho mẹ", "expect": {"event": "Gọi điện cho mẹ"}},

    # --- NHÓM 2: THỜI GIAN CỤ THỂ (GIỜ PHÚT) ---
    {"text": "Họp lúc 9h sáng", "expect": {"event": "Họp", "start": "09:00"}},
    {"text": "Đi xem phim lúc 19:30", "expect": {"event": "Đi xem phim", "start": "19:30"}},
    {"text": "Gặp khách hàng lúc 2h chiều", "expect": {"event": "Gặp khách hàng", "start": "14:00"}},
    {"text": "Đá bóng lúc 5 giờ rưỡi chiều", "expect": {"event": "Đá bóng", "start": "17:30"}},
    {"text": "Ăn sáng lúc 7g kém 15", "expect": {"event": "Ăn sáng", "start": "06:45"}},
    {"text": "Học bài lúc 23h đêm", "expect": {"event": "Học bài", "start": "23:00"}},
    {"text": "Tập gym vào 6h", "expect": {"event": "Tập gym", "start": "06:00"}},
    {"text": "Cafe lúc 20h", "expect": {"event": "Cafe", "start": "20:00"}},
    {"text": "Ngủ trưa lúc 12 rưỡi", "expect": {"event": "Ngủ", "start": "12:30"}}, 
    {"text": "Dậy lúc 5 am", "expect": {"event": "Dậy", "start": "05:00"}},

    # --- NHÓM 3: NGÀY THÁNG (TƯƠNG ĐỐI & TUYỆT ĐỐI) ---
    {"text": "Ngày mai đi phỏng vấn lúc 8h", "expect": {"event": "Đi phỏng vấn", "date": get_date_str(1), "start": "08:00"}},
    {"text": "Chiều mốt đi bơi", "expect": {"event": "Đi bơi", "date": get_date_str(2)}},
    {"text": "Thứ 2 tuần sau nộp báo cáo", "expect": {"event": "Nộp báo cáo", "date": get_weekday_date_str(0, 1)}},
    {"text": "Chủ nhật đi nhà thờ", "expect": {"event": "Đi nhà thờ", "date": get_weekday_date_str(6)}},
    {"text": "Sáng mai 9h đi họp", "expect": {"event": "Đi họp", "date": get_date_str(1), "start": "09:00"}},
    {"text": "Tối nay 7h đi chơi", "expect": {"event": "Đi chơi", "date": get_date_str(0), "start": "19:00"}},
    {"text": "Họp phụ huynh vào thứ 7", "expect": {"event": "Họp phụ huynh", "date": get_weekday_date_str(5)}},
    
    # --- NHÓM 4: ĐỊA ĐIỂM (LOCATION PARSER CHECK) ---
    {"text": "Đi siêu thị BigC", "expect": {"event": "Đi", "loc": "siêu thị BigC"}},
    {"text": "Học tiếng Anh ở trung tâm ILA", "expect": {"event": "Học tiếng Anh", "loc": "trung tâm ILA"}},
    {"text": "Đá bóng ở sân Thống Nhất", "expect": {"event": "Đá bóng", "loc": "sân Thống Nhất"}},
    {"text": "Gửi xe ở bãi giữ xe rạp phim", "expect": {"event": "Gửi xe", "loc": "bãi giữ xe rạp phim"}},
    {"text": "Đi bơi ở hồ bơi lam sơn", "expect": {"event": "Đi bơi", "loc": "hồ bơi Lam Sơn"}},
    {"text": "Thuê nhà ở ngõ 123 phố Huế", "expect": {"event": "Thuê nhà", "loc": "ngõ 123 phố Huế"}},
    {"text": "Về quê ăn tết", "expect": {"event": "Ăn tết", "loc": "quê"}},

    # --- NHÓM 5: KHOẢNG THỜI GIAN (DURATION & RANGE) ---
    {"text": "Học bài trong 2 tiếng", "expect": {"event": "Học bài", "dur": "2h"}},
    {"text": "Chạy bộ mất 30 phút", "expect": {"event": "Chạy bộ", "dur": "30p"}},
    {"text": "Họp từ 2h đến 4h chiều", "expect": {"event": "Họp", "start": "14:00", "end": "16:00", "dur": "2h"}},
    {"text": "Ca làm việc kéo dài 8 tiếng", "expect": {"event": "Ca làm việc", "dur": "8h"}},
    {"text": "Tập yoga 1 tiếng rưỡi", "expect": {"event": "Tập yoga", "dur": "1h30p"}},

    # --- NHÓM 6: THÓI QUEN (HABIT PARSER CHECK) ---
    {"text": "Đi tập gym mỗi sáng", "expect": {"event": "Đi tập gym", "habit": "DAILY"}},
    {"text": "Về thăm nhà mỗi tháng", "expect": {"event": "Về thăm nhà", "habit": "MONTHLY"}},
    {"text": "Đá bóng mỗi thứ 7", "expect": {"event": "Đá bóng", "habit": "WEEKLY"}},
    {"text": "Uống thuốc mỗi ngày", "expect": {"event": "Uống thuốc", "habit": "DAILY"}},

    # --- NHÓM 7: NHẮC NHỞ & TƯƠNG LAI (LOGIC KHÓ) ---
    # Lưu ý: "Sau 15 phút" sẽ tính Start time = Now + 15p. Test case này khó fix cứng giờ Start.
    # Nên ta chỉ check Reminder và Event Name.
    {"text": "Nhắc tôi uống thuốc sau 15 phút nữa", "expect": {"event": "Uống thuốc", "remind": "15 phút"}},
    {"text": "Họp lúc 9h nhắc trước 15 phút", "expect": {"event": "Họp", "start": "09:00", "remind": "15 phút"}},
    {"text": "Báo thức lúc 6h sáng mai", "expect": {"event": "Báo thức", "start": "06:00", "date": get_date_str(1)}},
    {"text": "Nhắc đi đón con lúc 4h chiều", "expect": {"event": "Đi đón con", "start": "16:00"}},
    {"text": "Báo tôi sớm 30p để chuẩn bị", "expect": {"event": "Chuẩn bị", "remind": "30 phút"}},

    # --- NHÓM 8: KẾT HỢP PHỨC TẠP (COMBO) ---
    {"text": "Đi siêu thị BigC vào lúc 9 giờ tối nay", "expect": {"event": "Đi", "loc": "siêu thị BigC", "start": "21:00", "date": get_date_str(0)}},
    {"text": "Học tiếng Anh ở trung tâm ILA mỗi tối thứ 2", "expect": {"event": "Học tiếng Anh", "loc": "trung tâm ILA", "habit": "WEEKLY"}},
    {"text": "Sáng mai 8h đưa con đi học ở trường tiểu học", "expect": {"event": "Đưa con đi học", "loc": "trường tiểu học", "start": "08:00", "date": get_date_str(1)}},
    {"text": "Chiều nay 5h rưỡi đi đá bóng ở sân Thống Nhất", "expect": {"event": "Đi đá bóng", "loc": "sân Thống Nhất", "start": "17:30"}},
    {"text": "Tập thể hình ở phòng Gym Cali trong 1 tiếng rưỡi", "expect": {"event": "Tập thể hình", "loc": "phòng Gym Cali", "dur": "1h30p"}},
    {"text": "Nhắc tôi đi mua quà tại cửa hàng lúc 10h sáng mai", "expect": {"event": "Đi mua quà", "loc": "cửa hàng", "start": "10:00", "date": get_date_str(1)}},
    {"text": "Họp team online lúc 14g chiều nay nhắc trước 10p", "expect": {"event": "Họp team online", "start": "14:00", "remind": "10 phút"}},

]

# ==============================================================================
# TEST RUNNER CLASS
# ==============================================================================
class TestRunner:
    def __init__(self):
        self.engine = NLPEngine()
        self.passed = 0
        self.failed = 0
        self.total = len(TEST_CASES)

    def run(self):
        print("\n" + "="*110)
        print(f"🚀 BẮT ĐẦU CHẤM ĐIỂM NLP ENGINE ({self.total} TEST CASES)")
        print(f"🕒 Thời gian test: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        print("="*110 + "\n")

        print(f"{'ID':<3} | {'INPUT':<45} | {'EVENT':<18} | {'ĐỊA ĐIỂM':<20} | {'BẮT ĐẦU':<8} | {'KẾT THÚC':<8} | {'HABIT':<8} | {'STATUS':<8} | {'CHI TIẾT LỖI (NẾU CÓ)'}")
        print("-" * 170)

        for i, case in enumerate(TEST_CASES, 1):
            input_text = case["text"]
            expected = case["expect"]
            
            # 1. Chạy Engine
            try:
                result = self.engine.process_command(input_text)
                
                # 2. Map kết quả thực tế sang format đơn giản để so sánh
                actual = self._map_result(result, expected)
                
                # >>> IN THÔNG TIN CHI TIẾT KẾT QUẢ PHÂN TÍCH <<<
                disp = result.get("display_data", {})
                data = result.get("data", {})
                event_name = data.get('event_name', '-')
                location = disp.get('location', '-')
                start = disp.get('start', '-')
                end = disp.get('end', '-')
                habit = disp.get('habit', '-')

                # 3. So sánh
                errors = self._compare(expected, actual)
                
                # 4. In kết quả
                status = "✅ PASS" if not errors else "❌ FAIL"
                if not errors:
                    self.passed += 1
                    error_msg = ""
                else:
                    self.failed += 1
                    error_msg = ", ".join(errors)

                # Format text cho đẹp
                display_text = (input_text[:42] + '..') if len(input_text) > 42 else input_text
                print(f"{i:<3} | {display_text:<45} | {event_name:<18} | {location:<20} | {start:<8} | {end:<8} | {habit:<8} | {status:<8} | {error_msg}")
    
            except Exception as e:
                self.failed += 1
                print(f"{i:<3} | {input_text:<45} | 💥 CRASH | {str(e)}")

        self._print_summary()

    def _map_result(self, result, expected_keys):
        """Map output của engine (display_data) về format của test case."""
        mapped = {}
        # Lấy display_data (dữ liệu đã format string đẹp)
        disp = result.get("display_data", {})
        data = result.get("data", {})
        
        # Mapping các trường
        if "event" in expected_keys: mapped["event"] = data.get("event_name", "")
        if "loc" in expected_keys: mapped["loc"] = disp.get("location", "-")
        if "start" in expected_keys: mapped["start"] = disp.get("start", "-")
        if "end" in expected_keys: mapped["end"] = disp.get("end", "-")
        if "date" in expected_keys: mapped["date"] = disp.get("date", "-")
        if "dur" in expected_keys: mapped["dur"] = disp.get("duration", "-")
        if "habit" in expected_keys: mapped["habit"] = disp.get("habit", "-")
        if "remind" in expected_keys: mapped["remind"] = disp.get("reminder", "-")
        
        return mapped

    def _compare(self, expected, actual):
        """So sánh Expected vs Actual. Trả về list các lỗi."""
        errors = []
        for key, exp_val in expected.items():
            act_val = actual.get(key, "---")
            
            # Chuẩn hóa để so sánh (lowercase, strip)
            exp_str = str(exp_val).lower().strip()
            act_str = str(act_val).lower().strip()
            
            # 1. So sánh Event Name (Mềm dẻo: chứa trong nhau là được)
            if key == "event":
                # Bỏ qua case hoa thường và khoảng trắng
                if exp_str != act_str:
                    # Nếu event name thực tế có chứa từ khóa chính của expect (hoặc ngược lại) -> Châm chước
                    if exp_str not in act_str and act_str not in exp_str:
                        errors.append(f"Event: Exp='{exp_val}' != Act='{act_val}'")
            
            # 2. So sánh Location (Mềm dẻo)
            elif key == "loc":
                if exp_str != act_str:
                     # "hồ bơi lam sơn" vs "hồ bơi" -> Coi như sai nếu mất tên riêng
                     # Nhưng "trung tâm ila" vs "ila" -> Có thể châm chước (tùy logic)
                     # Ở đây ta bắt chặt: phải khớp tương đối
                     if exp_str not in act_str:
                         errors.append(f"LOC: Exp='{exp_val}' != Act='{act_val}'")

            # 3. So sánh các trường khác (Cứng)
            else:
                # Fix lỗi Time --- vs -
                if exp_str == "---" and act_str == "-": continue 
                if exp_str == "-" and act_str == "---": continue
                
                if exp_str != act_str:
                    errors.append(f"{key.upper()}: Exp='{exp_val}' != Act='{act_val}'")
                    
        return errors

    def _print_summary(self):
        print("\n" + "="*100)
        score = (self.passed / self.total) * 100
        print(f"📊 KẾT QUẢ TỔNG KẾT")
        print(f"✅ Số câu đúng: {self.passed}")
        print(f"❌ Số câu sai:  {self.failed}")
        print(f"💯 ĐIỂM SỐ:     {score:.1f}/100")
        
        if score == 100:
            print("\n🏆 TUYỆT VỜI! ĐẠI CA ĐÃ CÓ MỘT CON BOT HOÀN HẢO!")
        elif score >= 90:
            print("\n🔥 XUẤT SẮC! Chỉ còn vài lỗi nhỏ xíu (nitpick).")
        elif score >= 70:
            print("\n👍 KHÁ TỐT! Bot đã hiểu được đa số các trường hợp.")
        else:
            print("\n⚠️ CẦN CỐ GẮNG! Hãy check lại logic parser.")
        print("="*100 + "\n")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run()