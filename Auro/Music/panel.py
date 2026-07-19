import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone
from Auro.Music.play import Player
from util.emojis import Emojis
from typing import cast

class Controls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="panel",
        description="🍎 Display the current song playing with control panels."
    )
    @commands.guild_only()
    @commands.cooldown(3,60, commands.BucketType.user)
    async def nowplaying(self, ctx: commands.Context):
        player = cast(Player, ctx.guild.voice_client)
        if ctx.guild.me.timed_out_until and ctx.guild.me.timed_out_until > datetime.now(timezone.utc):
            return
        if not player or not player.is_playing or not player.current:
            embed_error = discord.Embed(
                description=f"{Emojis.warning} There is no music playing right now.",
                color=discord.Color.red()
            )
            return await ctx.reply(
                embed=embed_error,
                ephemeral=True,
                delete_after=30
            )
        
        player.controller = ctx.channel
        
        music_cog = self.bot.get_cog("Music")
        if music_cog and hasattr(music_cog, "on_pomice_track_start"):
            await music_cog.on_pomice_track_start(player, player.current)

async def setup(bot: commands.Bot):
    await bot.add_cog(Controls(bot))