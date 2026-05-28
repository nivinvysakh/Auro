import sqlite3
from pathlib import Path

class SettingsStorage:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent / "DB" / "prefix.db"
        self.create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_prefixes (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT NOT NULL
                )
            """)
            
            
            try:
                cursor.execute("ALTER TABLE guild_prefixes ADD COLUMN channel_id INTEGER DEFAULT NULL")
            except sqlite3.OperationalError:
                pass  
                
            conn.commit()

    def get_prefix(self, guild_id: int) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT prefix FROM guild_prefixes WHERE guild_id = ?", (guild_id,))
            row = cursor.fetchone()
            return row[0] if row else "a!"

    def set_prefix(self, guild_id: int, prefix: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO guild_prefixes (guild_id, prefix) 
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET prefix = excluded.prefix
            """, (guild_id, prefix))
            conn.commit()
    
    def delete_prefix(self, guild_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM guild_prefixes WHERE guild_id = ?", (guild_id,))
            conn.commit()

    def get_allowed_channel(self, guild_id: int) -> int | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT channel_id FROM guild_prefixes WHERE guild_id = ?", (guild_id,))
            row = cursor.fetchone()
            return row[0] if row and row[0] is not None else None

    def set_allowed_channel(self, guild_id: int, channel_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
           
            cursor.execute("""
                INSERT INTO guild_prefixes (guild_id, prefix, channel_id) 
                VALUES (?, 'a!', ?)
                ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id
            """, (guild_id, channel_id))
            conn.commit()

    def remove_allowed_channel(self, guild_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE guild_prefixes 
                SET channel_id = NULL 
                WHERE guild_id = ?
            """, (guild_id,))
            conn.commit()

    async def init_db(self):
        self.create_tables()