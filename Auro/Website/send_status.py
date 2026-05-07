import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

class WebsiteStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = FastAPI()
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"], 
            allow_methods=["GET"],
        )

        self.stats_data = {"servers": 0, "users": 0, "online": True}

        self.app.add_api_route("/stats", self.get_stats, methods=["GET"])

        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        self.update_stats.start()

    async def get_stats(self):
        return self.stats_data

    def run_server(self):
        print(" [!] Website API is starting on http://localhost:8000")
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="error")

    @tasks.loop(minutes=5,reconnect=True)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        self.stats_data["servers"] = len(self.bot.guilds)
        self.stats_data["users"] = sum(g.member_count for g in self.bot.guilds if g.member_count)

    def cog_unload(self):
        self.update_stats.cancel()

async def setup(bot):
    await bot.add_cog(WebsiteStats(bot))