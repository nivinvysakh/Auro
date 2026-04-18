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

    async def clear_all(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM music_cache")
            await db.commit()
            await db.execute("VACUUM")

    async def clear_guild_cache(self, guild_id: int):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "DELETE FROM music_cache WHERE query = ?",
                (f"loop_{guild_id}",)
            )
            await db.commit()

    async def get_all(self):
        
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT query, track_hash, title FROM music_cache ORDER BY query") as cursor:
                return await cursor.fetchall()