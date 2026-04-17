import aiosqlite


DB_PATH = "databases/DB/music_storage.db"

class MusicStorage:
    def __init__(self):
        self.path = DB_PATH

    async def init_db(self):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS global_cache (
                    search_query TEXT PRIMARY KEY,
                    track_hash TEXT,
                    track_title TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def get_cached_track(self, query: str):
        
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                "SELECT track_hash, track_title FROM global_cache WHERE search_query = ?", 
                (query.strip().lower(),)
            ) as cursor:
                return await cursor.fetchone()

    async def save_to_storage(self, query: str, track_hash: str, title: str, source: str = "Unknown"):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO global_cache (search_query, track_hash, track_title, source) VALUES (?, ?, ?, ?)",
                (query.strip().lower(), track_hash, title, source)
            )
            await db.commit()
            