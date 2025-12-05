import sqlite3
from datetime import datetime, timedelta

# --- DTO CLASSES ---
class EventDto:
    def __init__(self, id, event_name, place, start_time, end_time, reminder_time, status):
        self.id = id
        self.event_name = event_name
        self.place = place
        self.start_time = start_time
        self.end_time = end_time
        self.reminder_time = reminder_time
        self.status = status
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.event_name,
            "start": self.start_time,
            "end": self.end_time,
            "extendedProps": {"location": self.place, "reminder": self.reminder_time}
        }

class HabitDto:
    # [UPDATE] Thêm current_streak và last_completed
    def __init__(self, id, habit_name, place, frequency, execution_time, reminder_time, status, current_streak, last_completed):
        self.id = id
        self.habit_name = habit_name
        self.place = place
        self.frequency = frequency
        self.execution_time = execution_time
        self.reminder_time = reminder_time
        self.status = status
        self.current_streak = current_streak
        self.last_completed = last_completed

# --- MANAGER ---
class EventManager:
    def __init__(self, db_name='data.db'):
        self.db_name = db_name
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        events_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eventName TEXT NOT NULL,
            place TEXT,
            startTime TEXT NOT NULL,
            endTime TEXT,
            reminderTime INTEGER,
            status TEXT NOT NULL CHECK (status IN ('active', 'inactive'))
        );"""
        
        # [UPDATE] Thêm cột currentStreak và lastCompleted
        habits_sql = """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habitName TEXT NOT NULL,
            place TEXT,
            frequency TEXT NOT NULL,
            executionTime TEXT,
            reminderTime INTEGER,
            status TEXT NOT NULL DEFAULT 'active',
            currentStreak INTEGER DEFAULT 0,
            lastCompleted TEXT -- Lưu ngày YYYY-MM-DD
        );"""
        try:
            with self._get_connection() as conn:
                conn.execute(events_sql)
                conn.execute(habits_sql)
                conn.commit()
        except sqlite3.Error as e:
            print(f"DB Init Error: {e}")

    # --- EVENTS (Giữ nguyên) ---
    def create_event(self, eventName, startTime, status="active", place=None, endTime=None, reminderTime=5):
        sql = "INSERT INTO events (eventName, place, startTime, endTime, reminderTime, status) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (eventName, place, startTime, endTime, reminderTime, status))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error: return None

    def get_all_events(self):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.cursor().execute("SELECT * FROM events ORDER BY startTime").fetchall()
                return [EventDto(
                    row["id"], row["eventName"], row["place"], row["startTime"], 
                    row["endTime"], row["reminderTime"], row["status"]
                ) for row in rows]
        except sqlite3.Error: return []
    def get_active_events(self):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.cursor().execute("SELECT * FROM events WHERE status='active' ORDER BY startTime").fetchall()
                return [EventDto(
                    row["id"], row["eventName"], row["place"], row["startTime"], 
                    row["endTime"], row["reminderTime"], row["status"]
                ) for row in rows]
        except sqlite3.Error: return []

    def get_event_by_id(self, event_id):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                row = conn.cursor().execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
                if row: return EventDto(row["id"], row["eventName"], row["place"], row["startTime"], row["endTime"], row["reminderTime"], row["status"])
        except sqlite3.Error: return None
        return None

    def delete_event(self, event_id):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error: return False

    def update_event(self, event_id, name, start_time, place, end_time, reminder_time, status):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE events
                SET eventName = ?, startTime = ?, place = ?, endTime = ?, reminderTime = ?, status = ?
                WHERE id = ?
            """, (name, start_time, place, end_time, reminder_time, status, event_id))
            conn.commit()

    def update_event_into_inactive(self, event_id,):
        status="inactive"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE events
                SET status = ?
                WHERE id = ?
            """, ( status, event_id))
            conn.commit()

    # --- HABITS (NÂNG CẤP LOGIC GIỮ LỬA) ---
    def create_habit(self, habitName, frequency, place=None, executionTime=None, reminderTime=5, status="active"):
        sql = "INSERT INTO habits (habitName, place, frequency, executionTime, reminderTime, status, currentStreak, lastCompleted) VALUES (?, ?, ?, ?, ?, ?, 0, NULL)"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (habitName, place, frequency, executionTime, reminderTime, status))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error: return None

    def get_all_habits(self):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.cursor().execute("SELECT * FROM habits ORDER BY id DESC").fetchall()
                
                habits = []
                for row in rows:
                    # [LOGIC] Kiểm tra xem có bị mất chuỗi không (Reset về 0 nếu lười biếng)
                    h_dto = HabitDto(
                        row["id"], row["habitName"], row["place"], row["frequency"],
                        row["executionTime"], row["reminderTime"], row["status"],
                        row["currentStreak"], row["lastCompleted"]
                    )
                    
                    # Logic kiểm tra và reset streak nếu quá hạn
                    if h_dto.last_completed:
                        last_date = datetime.strptime(h_dto.last_completed, "%Y-%m-%d").date()
                        today = datetime.now().date()
                        
                        should_reset = False
                        if h_dto.frequency == 'daily':
                            # Nếu hôm qua chưa làm (cách đây > 1 ngày) -> Mất chuỗi
                            if (today - last_date).days > 1:
                                should_reset = True
                        elif h_dto.frequency == 'weekly':
                            # Nếu tuần này và tuần trước đều chưa làm -> Mất chuỗi
                            # (Logic đơn giản: Cách quá 7 ngày + chênh lệch weekday)
                            # Tốt nhất: So sánh số tuần ISO
                            last_week = last_date.isocalendar()[1]
                            this_week = today.isocalendar()[1]
                            # Nếu cách nhau hơn 1 tuần -> Reset
                            if (this_week - last_week) > 1: 
                                should_reset = True
                        
                        if should_reset and h_dto.current_streak > 0:
                            # Cập nhật DB về 0
                            conn.execute("UPDATE habits SET currentStreak = 0 WHERE id = ?", (h_dto.id,))
                            conn.commit()
                            h_dto.current_streak = 0 # Update DTO trả về
                            
                    habits.append(h_dto)
                return habits
        except sqlite3.Error as e: 
            print(e)
            return []

    def delete_habit(self, habit_id):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error: return False

    # [MỚI] HÀM CHECK-IN GIỮ LỬA
    def check_in_habit(self, habit_id):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                row = cursor.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
                if not row: return False
                
                current_streak = row["currentStreak"]
                last_completed = row["lastCompleted"]
                freq = row["frequency"]
                
                today = datetime.now().date()
                today_str = today.strftime("%Y-%m-%d")
                
                # Nếu hôm nay đã làm rồi -> Không cộng thêm, chỉ báo OK
                if last_completed == today_str:
                    return True

                new_streak = current_streak
                
                if not last_completed:
                    # Lần đầu tiên làm
                    new_streak = 1
                else:
                    last_date = datetime.strptime(last_completed, "%Y-%m-%d").date()
                    
                    if freq == 'daily':
                        # Nếu làm hôm qua -> Tăng streak
                        if (today - last_date).days == 1:
                            new_streak += 1
                        # Nếu làm cách xa quá -> Reset về 1
                        else:
                            new_streak = 1
                            
                    elif freq == 'weekly':
                        # Check theo tuần ISO
                        this_week = today.isocalendar()[1]
                        last_week = last_date.isocalendar()[1]
                        
                        if this_week == last_week:
                            return True # Tuần này làm rồi
                        elif this_week - last_week == 1:
                            new_streak += 1
                        else:
                            new_streak = 1
                    
                    else: # Monthly/Yearly cứ cộng tạm
                        new_streak += 1

                # Cập nhật DB
                cursor.execute(
                    "UPDATE habits SET currentStreak = ?, lastCompleted = ? WHERE id = ?", 
                    (new_streak, today_str, habit_id)
                )
                conn.commit()
                return True
        
        except Exception as e:
            print(f"Check-in error: {e}")
            return False
    def export_all_data(self):
        """Lấy toàn bộ dữ liệu Events và Habits để xuất file"""
        data = {
            "events": [],
            "habits": []
        }
        
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 1. Lấy Events
                rows_event = cursor.execute("SELECT * FROM events").fetchall()
                for row in rows_event:
                    data["events"].append({
                        "id": row["id"],
                        "event_name": row["eventName"],
                        "place": row["place"],
                        "start_time": row["startTime"],
                        "end_time": row["endTime"],
                        "reminder_time": row["reminderTime"],
                        "status": row["status"]
                    })
                    
                # 2. Lấy Habits
                rows_habit = cursor.execute("SELECT * FROM habits").fetchall()
                for row in rows_habit:
                    data["habits"].append({
                        "id": row["id"],
                        "habit_name": row["habitName"],
                        "place": row["place"],
                        "frequency": row["frequency"],
                        "reminder_time": row["reminderTime"],
                        "status": row["status"],
                        "current_streak": row["currentStreak"],
                        "last_completed": row["lastCompleted"]
                    })
                    
            return data
        except sqlite3.Error as e:
            print(f"Export Error: {e}")
            return None