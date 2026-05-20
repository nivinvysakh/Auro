import discord
from discord.ext import commands
from discord import app_commands
from util.emojis import Emojis
from Auro.Music.play import Player
from typing import cast

class Seek(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
    
    def parse_time(self, time_str: str) -> int:
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    total_seconds = (minutes * 60) + seconds
                elif len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    total_seconds = (hours * 3600) + (minutes * 60) + seconds
            else:
                total_seconds = int(time_str)
            return total_seconds * 1000
        except ValueError:
            return -1
    
    def format_time(self, ms: int) -> str:
        seconds = int((ms / 1000) % 60)
        minutes = int((ms / (1000 * 60)) % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    @commands.hybrid_command(
        name="seek", description="🌊 Jump to a specific time in the song"
    )
    @commands.guild_only()
    @app_commands.describe(time="✨ Time to seek to (mm:ss or hh:mm:ss)")
    async def seek(self, ctx: commands.Context, time: str):
        player = cast(Player, ctx.voice_client)

        if not player :
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
                ) , delete_after=15
            )
        if not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Nothing is playing right now. Play a song first! `(￣ω￣;)`",
                    color=discord.Color.yellow()
                ) , delete_after=10 , ephemeral=True
            )
        if player.current.is_stream:
            embed=discord.Embed(
                    description=f"{Emojis.warning} `Seek` is not available for Radio",
                    color= discord.Color.yellow()
                )
            return await ctx.reply(
                embed=embed , delete_after=10 , ephemeral=True
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            return await ctx.reply(
                embed=embed , delete_after=10 , ephemeral=True
            )

        seek_ms = self.parse_time(time)

        if seek_ms < 0:
            return await ctx.reply(
                f"{Emojis.error} Invalid format. Use `mm:ss` or `hh:mm:ss`.",
                delete_after=5
            )
        if seek_ms > player.current.length:
            return await ctx.reply(
                embed= discord.Embed(
                    description=f"{Emojis.warning} Track limit exceeded.",
                    color= discord.Color.yellow()
                ) , delete_after=10
            )

        await player.seek(seek_ms)
        await ctx.reply(
            embed= discord.Embed(
                description=f"{Emojis.success} Seeked to {self.format_time(seek_ms)}.",
                color= discord.Color.green()
            ).set_author(name="Auro", icon_url=self.bot.user.avatar.url).set_thumbnail(url=player.current.thumbnail),delete_after=15
        )

async def setup(bot : commands.Bot):
    await bot.add_cog(Seek(bot))