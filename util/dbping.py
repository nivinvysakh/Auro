import aiosqlite
import time

async def get_db_ping(db_path="./database/DB/like.db"):
    start = time.perf_counter()

    async with aiosqlite.connect(db_path) as db:
        await db.execute("SELECT 1")  

    end = time.perf_counter()
    ping_ms = (end - start) * 1000 
    return round(ping_ms, 2)