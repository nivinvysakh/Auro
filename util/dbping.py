import aiosqlite
import time
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(CURRENT_DIR, ".."))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "databases", "DB", "badge.db")


async def get_db_ping(db_path=DEFAULT_DB_PATH):
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass

    start = time.perf_counter()

    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute("SELECT 1")
            
        end = time.perf_counter()
        ping_ms = (end - start) * 1000
        return round(ping_ms, 2)
        
    except Exception:
        return "ERR"