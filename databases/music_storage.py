import aiosqlite
import json

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
                    track_title TEXT UNIQUE,
                    search_query TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_query ON global_cache (search_query);"
            )
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_playlists (
                    user_id BIGINT,
                    playlist_name TEXT,
                    tracks_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, playlist_name)
                )
            """)
            await db.commit()

    async def get_cached_track(self, query: str):
        async with aiosqlite.connect(self.path) as db:
            clean_query = query.strip().lower()
            async with db.execute(
                "SELECT track_hash, track_title FROM global_cache WHERE search_query = ?", 
                (clean_query,)
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    return result
                
            async with db.execute(
                "SELECT track_hash, track_title FROM global_cache WHERE search_query LIKE ? LIMIT 1",
                (f"{clean_query}%",) 
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    return result
            return None

    async def get_by_track_hash(self, track_hash: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT track_title, source FROM global_cache WHERE track_hash = ?",
                (track_hash,),
            ) as cursor:
                return await cursor.fetchone()

    async def track_hash_exists(self, track_hash: str) -> bool:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT 1 FROM global_cache WHERE track_hash = ?",
                (track_hash,),
            ) as cursor:
                return await cursor.fetchone() is not None

    async def save_to_storage(self, query: str, track_hash: str, title: str, source: str = "Unknown"):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "INSERT OR IGNORE INTO global_cache (track_hash, search_query, track_title, source) VALUES (?, ?, ?, ?)",
                (track_hash, query.strip().lower(), title, source),
            )
            await db.commit()

    async def selective_flush(self, days: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "DELETE FROM global_cache WHERE created_at <= date('now', ?)",
                (f"-{days} days",),
            )
            await db.commit()
            await db.execute("VACUUM")

    async def flush_all(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("DELETE FROM global_cache")
            await db.commit()
            await db.execute("VACUUM")

    async def get_all(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT search_query, track_hash, track_title, source FROM global_cache ORDER BY created_at DESC"
            ) as cursor:
                return await cursor.fetchall()

    async def delete_by_title(self, song_name: str) -> int:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            clean_name = song_name.strip().lower()
            async with db.execute(
                "DELETE FROM global_cache WHERE LOWER(track_title) LIKE ? OR search_query LIKE ?",
                (f"%{clean_name}%", f"%{clean_name}%")
            ) as cursor:
                changes = cursor.rowcount
            await db.commit()
            await db.execute("VACUUM")
            return changes

    async def add_to_playlist(self, user_id: int, playlist_name: str, track_hash: str, track_title: str) -> bool:
        clean_pl_name = playlist_name.strip().lower()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT tracks_json FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                (user_id, clean_pl_name)
            ) as cursor:
                row = await cursor.fetchone()
            
            tracks = json.loads(row[0]) if row else []
            
            if any(t[0] == track_hash for t in tracks):
                return False
                
            tracks.append([track_hash, track_title])
            tracks_str = json.dumps(tracks)
            
            await db.execute(
                """INSERT INTO user_playlists (user_id, playlist_name, tracks_json, updated_at) 
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(user_id, playlist_name) 
                   DO UPDATE SET tracks_json = excluded.tracks_json, updated_at = CURRENT_TIMESTAMP""",
                (user_id, clean_pl_name, tracks_str)
            )
            await db.commit()
            return True

    async def delete_from_playlist(self, user_id: int, playlist_name: str, track_hash: str) -> bool:
        clean_pl_name = playlist_name.strip().lower()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT tracks_json FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                (user_id, clean_pl_name)
            ) as cursor:
                row = await cursor.fetchone()
                
            if not row:
                return False
                
            tracks = json.loads(row[0])
            initial_len = len(tracks)
            tracks = [t for t in tracks if t[0] != track_hash]
            
            if len(tracks) == initial_len:
                return False
                
            if not tracks:
                await db.execute(
                    "DELETE FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                    (user_id, clean_pl_name)
                )
            else:
                await db.execute(
                    "UPDATE user_playlists SET tracks_json = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND playlist_name = ?",
                    (json.dumps(tracks), user_id, clean_pl_name)
                )
            await db.commit()
            return True

    async def delete_entire_playlist(self, user_id: int, playlist_name: str) -> int:
        clean_pl_name = playlist_name.strip().lower()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT tracks_json FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                (user_id, clean_pl_name)
            ) as cursor:
                row = await cursor.fetchone()
                
            if not row:
                return 0
                
            tracks = json.loads(row[0])
            count = len(tracks)
            
            await db.execute(
                "DELETE FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                (user_id, clean_pl_name)
            )
            await db.commit()
            await db.execute("VACUUM")
            return count

    async def get_user_playlist(self, user_id: int, playlist_name: str) -> list:
        clean_pl_name = playlist_name.strip().lower()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT tracks_json FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                (user_id, clean_pl_name)
            ) as cursor:
                row = await cursor.fetchone()
                
            return json.loads(row[0]) if row else []

    async def get_playlist_track_count(self, user_id: int, playlist_name: str) -> int:
        clean_pl_name = playlist_name.strip().lower()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT tracks_json FROM user_playlists WHERE user_id = ? AND playlist_name = ?",
                (user_id, clean_pl_name)
            ) as cursor:
                row = await cursor.fetchone()
                
            if not row:
                return 0
                
            return len(json.loads(row[0]))

    async def get_all_user_playlists(self, user_id: int) -> list:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT playlist_name, tracks_json FROM user_playlists WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()