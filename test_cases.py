import sys
import os
from datetime import datetime

# Cấu hình đường dẫn
sys.path.append(os.path.join(os.path.dirname(__file__), 'nlp'))
try:
    from nlp.nlp_engine import NLPEngine
except ImportError:
    print("❌ Lỗi: Không tìm thấy module nlp_engine!")
    sys.exit(1)

class TestBenchmark:
    def __init__(self):
        self.engine = NLPEngine()
        self.passed_tests = 0
        
        # --- BỘ 30 TEST CASE CHUẨN (CÓ THÊM EXPECTED DURATION) ---
        self.test_cases = [
            # NHÓM 1: CƠ BẢN
            {"input": "Họp team ở Quận 1 lúc 9h sáng", "exp_evt": "họp team", "exp_loc": "quận 1", "exp_start": "09:00", "exp_dur": None},
            {"input": "Đi đá banh tại sân Thống Nhất chiều nay 17h", "exp_evt": "đi đá banh", "exp_loc": "sân thống nhất", "exp_start": "17:00", "exp_dur": None},
            {"input": "Gặp khách hàng tại Highland Coffee lúc 10:30", "exp_evt": "gặp khách hàng", "exp_loc": "highland coffee", "exp_start": "10:30", "exp_dur": None},
            {"input": "Tối nay 19h đi ăn lẩu ở Hadilao", "exp_evt": "đi ăn lẩu", "exp_loc": "hadilao", "exp_start": "19:00", "exp_dur": None},
            {"input": "Về quê ở Cần Thơ ăn tết", "exp_evt": "quê ăn tết", "exp_loc": "cần thơ", "exp_start": None, "exp_dur": None},

            # NHÓM 2: TEENCODE & KHÔNG DẤU
            {"input": "mai di da banh vs nhom o q7", "exp_evt": "đi đá banh với nhóm", "exp_loc": "quận 7", "exp_start": None, "exp_dur": None},
            {"input": "hqua t di hoc muon qua", "exp_evt": "đi học muộn quá", "exp_loc": None, "exp_start": None, "exp_dur": None},
            {"input": "toi nay 7h ranh ko", "exp_evt": "rảnh không", "exp_loc": None, "exp_start": "19:00", "exp_dur": None},
            {"input": "hn dang mua to o ha noi", "exp_evt": "đang mưa to", "exp_loc": "hà nội", "exp_start": None, "exp_dur": None},
            {"input": "tmai co vc di q9 ko b?", "exp_evt": "có việc", "exp_loc": "quận 9", "exp_start": None, "exp_dur": None},

            # NHÓM 3: THỜI GIAN PHỨC TẠP
            {"input": "Học bài từ 8h đến 10h sáng", "exp_evt": "học bài", "exp_loc": None, "exp_start": "08:00", "exp_end": "10:00", "exp_dur": "2h0p"},
            {"input": "Chạy bộ trong 30 phút", "exp_evt": "chạy bộ", "exp_loc": None, "exp_dur": "0h30p"},
            {"input": "Làm việc từ 13h tới giờ", "exp_evt": "làm việc", "exp_loc": None, "exp_start": "13:00", "exp_end": datetime.now().strftime("%H:%M")},
            {"input": "Gặp nhau lúc 10h kém 15", "exp_evt": "gặp nhau", "exp_loc": None, "exp_start": "09:45", "exp_dur": None},
            {"input": "Ngủ từ 23h đến 6h sáng hôm sau", "exp_evt": "ngủ", "exp_loc": None, "exp_start": "23:00", "exp_end": "06:00", "exp_dur": "7h0p"},

            # NHÓM 4: NHẮC NHỞ
            {"input": "Họp lúc 9h nhắc trước 15p", "exp_evt": "họp", "exp_remind": 15, "exp_start": "09:00", "exp_dur": None},
            {"input": "Báo sớm 30 phút đi đón con lúc 4h chiều", "exp_evt": "đi đón con", "exp_remind": 30, "exp_start": "16:00", "exp_dur": None},
            {"input": "Nhắc tôi uống thuốc lúc 20h", "exp_evt": "tôi uống thuốc", "exp_loc": None, "exp_start": "20:00", "exp_dur": None},
            {"input": "Gọi điện cho mẹ lúc 7h tối báo trước 5p", "exp_evt": "gọi điện cho mẹ", "exp_remind": 5, "exp_start": "19:00", "exp_dur": None},
            {"input": "Set kèo đi nhậu nhắc sớm 1 tiếng", "exp_evt": "thiết lập kèo đi nhậu", "exp_remind": 60, "exp_dur": None},

            # NHÓM 5: THÓI QUEN
            {"input": "Đi tập gym mỗi ngày", "exp_evt": "đi tập gym", "exp_habit": "daily"},
            {"input": "Họp giao ban hàng tuần vào thứ 2", "exp_evt": "họp giao ban", "exp_habit": "weekly"},
            {"input": "Trả tiền nhà hàng tháng", "exp_evt": "trả tiền nhà", "exp_habit": "monthly"},
            {"input": "Đi bơi mỗi chiều chủ nhật", "exp_evt": "đi bơi", "exp_habit": "weekly"},
            {"input": "Check mail mỗi sáng", "exp_evt": "check mail", "exp_habit": "daily"},

            # NHÓM 6: ĐỊA ĐIỂM KHÓ
            {"input": "Nhà ở đường Nguyễn Văn Cừ Quận 5", "exp_evt": "sự kiện mới", "exp_loc": "đường nguyễn văn cừ quận 5"},
            {"input": "Căn hộ Landmark 81 tầng 3", "exp_evt": "sự kiện mới", "exp_loc": "căn hộ landmark 81 tầng 3"},
            {"input": "Ra công viên tập thể dục", "exp_evt": "tập thể dục", "exp_loc": "công viên"},
            {"input": "Đi siêu thị mua đồ", "exp_evt": "mua đồ", "exp_loc": "siêu thị"}, 
            {"input": "Đợi ở bãi gửi xe", "exp_evt": "đợi", "exp_loc": "bãi gửi xe"},
            {"input": "mỗi tuần đều đi bộ buổi sáng", "exp_evt": "đi bộ buổi sáng", "exp_loc": "-"},
            {"input": "đi bộ buổi sáng mỗi tuần", "exp_evt": "đi bộ buổi sáng", "exp_loc": "-"}
        ]

    def _normalize_str(self, s):
        if not s or s == "-": return None
        return str(s).lower().strip()

    def run(self):
        print("\n" + "="*60)
        print("🚀 KẾT QUẢ TEST BENCHMARK (FULL DURATION)...")
        print("="*60)

        for i, case in enumerate(self.test_cases, 1):
            raw = case["input"]
            res = self.engine.process_command(raw)
            d = res['data']
            t = d['time']
            
            # Lấy dữ liệu thực tế
            act_event = d['event_name']
            act_loc = d['location'] if d['location'] else "-"
            act_remind = d['reminder']
            act_habit = d['habit'] if d['habit'] else "-"
            
            # Xử lý Time
            act_date = "-"
            if t.get('date'): act_date = t['date'].strftime("%d/%m/%Y")

            act_start = None
            if t.get('start_time'):
                act_start = f"{t['start_time']['hour']:02}:{t['start_time']['minute']:02}"
            
            act_end = None
            if t.get('end_time'):
                act_end = f"{t['end_time']['hour']:02}:{t['end_time']['minute']:02}"

            # Xử lý Duration
            act_dur = None
            if t.get('duration'):
                total = int(t['duration'].total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                act_dur = f"{h}h{m}p"

            # --- LOGIC CHẤM ĐIỂM ---
            is_pass = True
            
            if "exp_loc" in case and self._normalize_str(act_loc) != self._normalize_str(case["exp_loc"]): is_pass = False
            if "exp_habit" in case and self._normalize_str(act_habit) != self._normalize_str(case["exp_habit"]): is_pass = False
            if "exp_remind" in case and act_remind != case["exp_remind"]: is_pass = False
            if "exp_start" in case and act_start != case["exp_start"]: is_pass = False
            if "exp_end" in case and act_end != case["exp_end"]: is_pass = False
            if "exp_dur" in case and act_dur != case["exp_dur"]: is_pass = False

            if is_pass: self.passed_tests += 1
            status_icon = "✅ PASS" if is_pass else "❌ FAIL"

            # --- IN KẾT QUẢ DỌC ---
            print(f"\n🔹 CASE {i}: {raw}")
            
            def print_line(label, actual, expected, check):
                mark = "" if check else "  <-- SAI (Mong đợi: " + str(expected) + ")"
                print(f"   {label:<10} {str(actual):<25} {mark}")

            print_line("Event:", act_event, case.get('exp_evt'), True)
            print_line("Date:", act_date, "-", True)
            
            if "exp_loc" in case or act_loc != "-":
                check_loc = self._normalize_str(act_loc) == self._normalize_str(case.get('exp_loc'))
                print_line("Location:", act_loc, case.get('exp_loc', '-'), check_loc)
            
            if "exp_start" in case or act_start:
                check_start = act_start == case.get('exp_start')
                print_line("Start:", str(act_start), case.get('exp_start', '-'), check_start)

            if "exp_end" in case or act_end:
                check_end = act_end == case.get('exp_end')
                print_line("End:", str(act_end), case.get('exp_end', '-'), check_end)

            if "exp_dur" in case or act_dur:
                check_dur = act_dur == case.get('exp_dur')
                print_line("Duration:", str(act_dur), case.get('exp_dur', '-'), check_dur)

            if "exp_remind" in case or act_remind:
                check_rem = act_remind == case.get('exp_remind')
                print_line("Remind:", f"{act_remind}p" if act_remind else "-", case.get('exp_remind'), check_rem)
                
            if "exp_habit" in case or act_habit != "-":
                check_hab = self._normalize_str(act_habit) == self._normalize_str(case.get('exp_habit'))
                print_line("Habit:", act_habit, case.get('exp_habit', '-'), check_hab)

            print(f"   => {status_icon}")
            print("-" * 60)

        # TỔNG KẾT
        score = (self.passed_tests / 30) * 10
        print("\n" + "="*60)
        print(f"📊 TỔNG KẾT ĐIỂM SỐ:")
        print(f"   - Đạt: {self.passed_tests} / 30")
        print(f"   - Điểm: {score:.1f} / 10")
        print("="*60)

if __name__ == "__main__":
    tester = TestBenchmark()
    tester.run()
    