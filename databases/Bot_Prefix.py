import aiosqlite
class PrefixDatabase:
    def __init__(self, db_path="./database/DB/prefix.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS guild_prefixes (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT
                )
                """
            )
            await db.commit()

    async def set_prefix(self, guild_id, prefix):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO guild_prefixes (guild_id, prefix) VALUES (?, ?)",
                (guild_id, prefix),
            )
            await db.commit()

    async def get_prefix(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT prefix FROM guild_prefixes WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else '!'
            
    async def reset_prefix(self,guild_id:int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM guild_prefixes WHERE guild_id = ?",
                (guild_id,)
            )
            await db.commit()