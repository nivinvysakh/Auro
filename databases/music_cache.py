import aiosqlite


DB_PATH = "databases/DB/music_cache.db"

class MusicCache:
    def __init__(self):
        self.path = DB_PATH

    async def init_db(self):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA journal_mode=WAL;") 
            await db.execute("PRAGMA synchronous=NORMAL;")
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
            await db.execute("PRAGMA synchronous=NORMAL;")
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT track_hash FROM music_cache WHERE query = ?", 
                (query.strip().lower(),)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set_cached_hash(self, query: str, track_hash: str, title: str):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "INSERT OR REPLACE INTO music_cache (query, track_hash, title) VALUES (?, ?, ?)",
                (query.strip().lower(), track_hash, title)
            )
            await db.commit()

    async def clear_all(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("DELETE FROM music_cache")
            await db.commit()
            await db.execute("VACUUM")

    async def clear_guild_cache(self, guild_id: int):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "DELETE FROM music_cache WHERE query = ?",
                (f"loop_{guild_id}".lower(),)
            )
            await db.commit()

    async def clear_guild_cache_by_query(self, query: str):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "DELETE FROM music_cache WHERE query = ?",
                (query.strip().lower(),)
            )
            await db.commit()
    async def clear_all_guild_cache(self, guild_id: int):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "DELETE FROM music_cache WHERE query LIKE ?",
                (f"%{guild_id}%",)
            )
            await db.commit()
    async def clear_loop_queue(self, guild_id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            query_pattern = f"loop_queue_{guild_id}_%"
            await db.execute(
                "DELETE FROM music_cache WHERE query LIKE ?",
                (query_pattern,)
            )
            await db.commit()
    async def get_all(self):
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute("SELECT query, track_hash, title FROM music_cache ORDER BY query") as cursor:
                return await cursor.fetchall()