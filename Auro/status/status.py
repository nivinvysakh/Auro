import discord
from discord.ext import commands, tasks
import random
import datetime
import asyncio
class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_loop.start()
        self.event_check.start()

    def cog_unload(self):
        self.status_loop.cancel()
        self.event_check.cancel()

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
            discord.Activity(type=discord.ActivityType.listening, name="Good For You x One Of the Girls 🎧"),
            discord.Activity(type=discord.ActivityType.listening, name="After Dark 🌕"),
            discord.Activity(type=discord.ActivityType.listening, name="Fairytale 🪽"),
            discord.Activity(type=discord.ActivityType.custom, name="Auro", state="🍃"),
            discord.Activity(type=discord.ActivityType.custom, name="Auro", state="🌛")
        ]

        status_item = random.choice(activities)
        
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=status_item
        )
        
    @tasks.loop(hours=24.0,reconnect=True)
    async def event_check(self):
        now_date = datetime.datetime.now(datetime.UTC)
        if now_date.month == 12 and now_date.day == 25:
            if self.status_loop.is_running():
                self.status_loop.stop()
                print(f"{self.bot.get_time()} | INFO      | Standard loop stopped. Cooling down...")
                await asyncio.sleep(10)
            await self.bot.change_presence(
                status=discord.Status.do_not_disturb,
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name="Christmas in Hollis 🎄"
                )
            )
            print(f"{self.bot.get_time()} | EVENT     | DND Holiday Status Engaged.")
        elif (now_date.month == 12 and now_date.day == 31) or (now_date.month == 1 and now_date.day == 1):
            if self.status_loop.is_running():
                self.status_loop.stop()
                print(f"{self.bot.get_time()} | INFO      | Standard loop stopped. Cooling down...")
                await asyncio.sleep(10)
            await self.bot.change_presence(
                status=discord.Status.idle,
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="Happy New Year 🎉"
                )
            )
            print(f"{self.bot.get_time()} | EVENT     | New Year Eve Triggered .")
        elif now_date.month == 11 and now_date.day == 19 :
            if self.status_loop.is_running():
                self.status_loop.stop()
                await asyncio.sleep(10)
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity= discord.Activity(
                    type= discord.ActivityType.watching,
                    name = "Eclipse 🎂"
                )
            )
            print(f"{self.bot.get_time()} | EVENT     | Bday Triggered .")
        else :
            if not self.status_loop.is_running():
                self.status_loop.start()
    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StatusCog(bot))