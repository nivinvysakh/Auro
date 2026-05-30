import sqlite3
import os
from pathlib import Path

class TrackingStorage:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent / "DB" / "tracking.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_lifetime (
                    user_id INTEGER PRIMARY KEY,
                    total_seconds REAL DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_sessions (
                    user_id INTEGER PRIMARY KEY,
                    join_timestamp REAL
                )
            """)
            conn.commit()
            

    def start_session(self, user_id: int, timestamp: float):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM active_sessions WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return
            
            cursor.execute(
                "INSERT OR REPLACE INTO active_sessions (user_id, join_timestamp) VALUES (?, ?)",
                (user_id, timestamp)
            )
            conn.commit()
            

    def end_session(self, user_id: int, leave_timestamp: float) -> float:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT join_timestamp FROM active_sessions WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return 0.0  
            
            join_timestamp = row[0]
            session_seconds = leave_timestamp - join_timestamp
            
            cursor.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))

            cursor.execute("""
                INSERT INTO voice_lifetime (user_id, total_seconds) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET total_seconds = total_seconds + EXCLUDED.total_seconds
            """, (user_id, session_seconds))
            conn.commit()
            
            return session_seconds

    def get_lifetime_hours(self, user_id: int) -> float:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT total_seconds FROM voice_lifetime WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                calculated_hours = round(row[0] / 3600, 1)
                return calculated_hours
            
            return 0.0

    async def init_db(self):
        self.create_tables()