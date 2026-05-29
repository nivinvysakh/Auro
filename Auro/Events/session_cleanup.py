import time
from discord.ext import commands
import sqlite3
from databases.tracking import TrackingStorage

class SessionCleanup(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.storage = TrackingStorage()
        self.boot_time = time.time()

    @commands.Cog.listener()
    async def on_ready(self):
        flushed_count = 0

        with sqlite3.connect(self.storage.db_path) as conn:
            cursor = conn.cursor()
            try:
                
                cursor.execute("SELECT user_id FROM active_sessions WHERE join_timestamp < ?", (self.boot_time,))
                stuck_sessions = cursor.fetchall()

                if stuck_sessions:
                    for row in stuck_sessions:
                        user_id = row[0]
                        self.storage.end_session(user_id, self.boot_time)
                        flushed_count += 1
            except Exception as e:
                print(f"[CLEANUP CRASH] Routine hit a brick wall: {e}")


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(SessionCleanup(bot))