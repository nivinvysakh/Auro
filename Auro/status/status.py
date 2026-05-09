import discord
from discord.ext import commands, tasks
import random

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    @tasks.loop(hours=1.0,reconnect=True)
    async def status_loop(self):
        activities = [
            discord.Activity(type=discord.ActivityType.listening, name="The Kill 2 💝"),
            discord.Activity(type=discord.ActivityType.listening, name="SICKO MODE 🕺"),
            discord.Activity(type=discord.ActivityType.listening, name="4X4 🚤"),
            discord.Activity(type=discord.ActivityType.listening, name="Rupture 🎷"),
            discord.Activity(type=discord.ActivityType.listening, name="La Da dee 🏄‍♂️"),
            discord.Activity(type=discord.ActivityType.listening, name="Dracula 🧛"),
            discord.Activity(type=discord.ActivityType.listening, name="Cali Man 😎"),
            discord.Activity(type=discord.ActivityType.listening, name="Paradise 🐻‍❄️"),
            discord.Activity(type=discord.ActivityType.listening, name="Ransom 🔏"),
            discord.Activity(type=discord.ActivityType.custom, name="Auro", state="🍃")
        ]

        status_item = random.choice(activities)
        
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=status_item
        )
        
        print(f"{self.bot.get_time()} | SUCCESS   | Status Rotated: {status_item.name if hasattr(status_item, 'name') else status_item.state}")

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StatusCog(bot))