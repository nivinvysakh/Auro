import firebase_admin
from firebase_admin import credentials, firestore
from discord.ext import commands, tasks

class FirestoreStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.update_firestore.start()

    @tasks.loop(seconds=30 , reconnect=True)
    async def update_firestore(self):
        await self.bot.wait_until_ready()
        
        stats = {
            "servers": len(self.bot.guilds),
            "users": sum(g.member_count for g in self.bot.guilds if g.member_count),
            "sessions": len(self.bot.voice_clients),
            "last_updated": firestore.SERVER_TIMESTAMP
        }
        
        
        self.db.collection("bot").document("stats").set(stats)

async def setup(bot):
    await bot.add_cog(FirestoreStats(bot))