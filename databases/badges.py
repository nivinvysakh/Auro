import aiosqlite
import json


class BadgesDatabase:
    def __init__(self, db_path=r"./databases\DB\badge.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS badges (
                    user_id INTEGER PRIMARY KEY,
                    badges TEXT DEFAULT '[]'
                )
            """)
            await db.commit()

    async def add_badge(self, user_id: int, badge: str):
        badges = await self.get_badges(user_id)
        if badge not in badges:
            badges.append(badge)
            await self._save_badges(user_id, badges)

    async def remove_badge(self, user_id: int, badge: str):
        badges = await self.get_badges(user_id)
        if badge in badges:
            badges.remove(badge)
            await self._save_badges(user_id, badges)

    async def get_badges(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute(
                "SELECT badges FROM badges WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return []
                return json.loads(row[0])

    async def set_badges(self, user_id: int, badges: list[str]):
        await self._save_badges(user_id, badges)

    async def remove_user(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("DELETE FROM badges WHERE user_id = ?", (user_id,))
            await db.commit()

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            async with db.execute("SELECT user_id, badges FROM badges") as cursor:
                rows = await cursor.fetchall()
                return [
                    {"user_id": row[0], "badges": json.loads(row[1])} for row in rows
                ]

    async def _save_badges(self, user_id: int, badges: list[str]):
        badges_json = json.dumps(badges)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute(
                "INSERT OR REPLACE INTO badges (user_id, badges) VALUES (?, ?)",
                (user_id, badges_json),
            )
            await db.commit()
