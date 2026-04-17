import aiosqlite


DB_PATH = "databases/DB/music_cache.db"

class MusicCache:
    def __init__(self):
        self.path = DB_PATH

    async def init_db(self):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS music_cache (
                    query TEXT PRIMARY KEY,
                    track_hash TEXT,
                    title TEXT
                )
            """)
            await db.commit()


    async def get_cached_hash(self, query: str) -> str:
       
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                "SELECT track_hash FROM music_cache WHERE query = ?", 
                (query.strip().lower(),)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set_cached_hash(self, query: str, track_hash: str, title: str):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO music_cache (query, track_hash, title) VALUES (?, ?, ?)",
                (query.strip().lower(), track_hash, title)
            )
            await db.commit()