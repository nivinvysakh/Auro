import discord
from discord.ext import commands
import pomice
import asyncio
from util.emojis import Emojis
from typing import cast

class Player(pomice.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = pomice.Queue()
        self.controller = None 

    async def do_next(self):
        if self.is_playing or self.queue.is_empty:
            return
        
        try:
            track = self.queue.get()
            await self.play(track)
        except Exception:
            pass

class Inactivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id == self.bot.user.id:
            if before.channel and not after.channel:
                player = cast(Player, member.guild.voice_client)
                if player:
                    await player.destroy()
            return

        player = cast(Player, member.guild.voice_client)
        if not player or not player.channel:
            return

        if len(player.channel.members) == 1:
            await asyncio.sleep(120) 
            if len(player.channel.members) == 1:
                if player.controller:
                    embed = discord.Embed(
                        description=f"{Emojis.warning} **Disconnected:** No listeners detected.",
                        color=discord.Color.dark_grey()
                    )
                    await player.controller.send(embed=embed, delete_after=20)
                await player.destroy()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        mentions = (f"<@!{self.bot.user.id}>", f"<@{self.bot.user.id}>")
        if not message.content.startswith(mentions):
            return

        parts = message.content.split()
        if len(parts) < 3:
            return 

        trigger = parts[1].lower()
        search_query = " ".join(parts[2:])
        play_aliases = ['play', 'p', 'py', 'pl']

        if trigger in play_aliases:
            ctx = await self.bot.get_context(message)
            if not ctx.author.voice :
                return
            
            music_cog = self.bot.get_cog("Music")
            
            if music_cog:
                await music_cog.play.callback(music_cog, ctx, search=search_query)

async def setup(bot):
    await bot.add_cog(Inactivity(bot))