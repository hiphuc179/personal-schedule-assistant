import sqlite3

class EventManager:

    
    def __init__(self, db_name='data.db'):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eventName TEXT NOT NULL,
            place TEXT,
            startTime TEXT NOT NULL, -- ISO 8601 format
            endTime TEXT,
            reminderTime INTEGER, -- Minutes before start time
            status TEXT NOT NULL CHECK (status IN ('active', 'inactive'))
        );
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error during table creation: {e}")

    def create_event(self, eventName, startTime, status="active", place=None, endTime=None, reminderTime=5):
        insert_sql = """
        INSERT INTO events (eventName, place, startTime, endTime, reminderTime, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        data = (eventName, place, startTime, endTime, reminderTime, status)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, data)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating event: {e}")
            return None

    def get_all_events(self):
        select_sql = "SELECT * FROM events ORDER BY startTime"
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row 
                cursor = conn.cursor()
                cursor.execute(select_sql)
                rows = cursor.fetchall()
                return [
                    EventDto(
                        id=row["id"],
                        event_name=row["eventName"],
                        place=row["place"],
                        start_time=row["startTime"],
                        end_time=row["endTime"],
                        reminder_time=row["reminderTime"],
                        status=row["status"]
                    )
                    for row in rows
                ]
        except sqlite3.Error as e:
            print(f"Error fetching events: {e}")
            return []
        
    def get_event_by_id(self, event_id):
        select_sql = "SELECT * FROM events WHERE id = ?"
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(select_sql, (event_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                return EventDto(
                    id=row["id"],
                    event_name=row["eventName"],
                    place=row["place"],
                    start_time=row["startTime"],
                    end_time=row["endTime"],
                    reminder_time=row["reminderTime"],
                    status=row["status"]
                )
        except sqlite3.Error as e:
            print(f"Error fetching event ID {event_id}: {e}")
            return None
        
    def update_event(self,eventId, eventName, startTime, place, endTime, reminderTime,status):
        sql = """
            UPDATE events SET eventName = ?, place = ?, startTime = ?, endTime = ?, reminderTime = ?, status = ?
            WHERE id = ?
        """
        data = (eventName, place, startTime, endTime, reminderTime, status, eventId)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating event ID {eventId}: {e}")
            return None

        
    def update_event_status(self, event_id, new_status):
        update_sql = "UPDATE events SET status = ? WHERE id = ?"
        data = (new_status, event_id)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, data)
                conn.commit()
                return cursor.rowcount > 0 
        except sqlite3.Error as e:
            print(f"Error updating event ID {event_id}: {e}")
            return False

    def delete_event(self, event_id):
        delete_sql = "DELETE FROM events WHERE id = ?"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_sql, (event_id,))
                conn.commit()
                return cursor.rowcount > 0 
        except sqlite3.Error as e:
            print(f"Error deleting event ID {event_id}: {e}")
            return False
    
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
            "id": self.id,
            "eventName": self.event_name,
            "place": self.place,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "reminderTime": self.reminder_time,
            "status": self.status
        }

    def __repr__(self):
        return f"<EventDto id={self.id} event_name={self.event_name} start_time={self.start_time}>"