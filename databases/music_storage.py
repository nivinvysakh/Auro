import aiosqlite

DB_PATH = "databases/DB/music_storage.db"


class MusicStorage:
    def __init__(self):
        self.path = DB_PATH

    async def init_db(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")

            await db.execute("""
                CREATE TABLE IF NOT EXISTS global_cache (
                    track_hash TEXT PRIMARY KEY,
                    track_title TEXT,
                    search_query TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_query
                ON global_cache (search_query)
            """)

            await db.commit()


    def normalize(self, query: str) -> str:
        query = query.lower().strip()
        query = query.split(" - ")[0]
        query = query.split("|")[0]
        return " ".join(query.split())


    def score_match(self, query_words, stored_query: str) -> int:
        stored_words = stored_query.split()

        score = 0
        for w in query_words:
            for s in stored_words:
                if w in s or s in w:
                    score += 1
                    break

        return score


    async def get_cached_track(self, query: str):
        query = self.normalize(query)
        words = query.split()

        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA synchronous=NORMAL;")


            async with db.execute(
                """
                SELECT track_hash, track_title, search_query
                FROM global_cache
                WHERE search_query = ?
                """,
                (query,),
            ) as cursor:
                exact = await cursor.fetchone()

            if exact:
                return exact["track_hash"], exact["track_title"]


            like_clause = " OR ".join(["search_query LIKE ?"] * len(words))
            values = [f"%{w}%" for w in words]

            async with db.execute(
                f"""
                SELECT track_hash, track_title, search_query
                FROM global_cache
                WHERE {like_clause}
                LIMIT 25
                """,
                values,
            ) as cursor:
                rows = await cursor.fetchall()

            if not rows:
                return None


            best = None
            best_score = 0

            for row in rows:
                score = self.score_match(words, row["search_query"])

                if score > best_score:
                    best_score = score
                    best = (row["track_hash"], row["track_title"])


            if best and best_score >= 1:
                return best

            return None


    async def get_by_track_hash(self, track_hash: str):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                """
                SELECT track_title, source
                FROM global_cache
                WHERE track_hash = ?
                """,
                (track_hash,),
            ) as cursor:
                return await cursor.fetchone()

    async def track_hash_exists(self, track_hash: str) -> bool:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                "SELECT 1 FROM global_cache WHERE track_hash = ?",
                (track_hash,),
            ) as cursor:
                return await cursor.fetchone() is not None


    async def save_to_storage(self, query: str, track_hash: str, title: str, source: str = "Unknown"):
        query = self.normalize(query)

        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO global_cache
                (track_hash, search_query, track_title, source)
                VALUES (?, ?, ?, ?)
                """,
                (track_hash, query, title, source),
            )
            await db.commit()


    async def get_all(self):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(
                """
                SELECT search_query, track_hash, track_title, source
                FROM global_cache
                ORDER BY created_at DESC
                """
            ) as cursor:
                return await cursor.fetchall()

    async def selective_flush(self, days: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "DELETE FROM global_cache WHERE created_at <= date('now', ?)",
                (f"-{days} days",),
            )
            await db.commit()

    async def flush_all(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM global_cache")
            await db.commit()