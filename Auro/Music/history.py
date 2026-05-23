import discord
from discord.ext import commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class History(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="history",
        description="📜 View the last 10 tracks played in this session.",
        aliases=["his"]
    )
    @commands.guild_only()
    async def history(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color=discord.Color.yellow()
            )
            return await ctx.reply(embed=embed, delete_after=10)
            
        player = cast(Player, ctx.voice_client)
        
        if not player.history or len(player.history) < 2:
            embed = discord.Embed(
                title=f"{Emojis.warning} The history is currently empty!",
                description="`(￣ω￣;)`",
                color=discord.Color.yellow()
            )
            return await ctx.reply(embed=embed, delete_after=10)
        
        history_list = list(player.history)
        if player.is_playing:
            played_tracks = history_list[:-1]
        else :
            played_tracks = history_list
        played_tracks.reverse()
        
        description_text = ""
        for i, track in enumerate(played_tracks, 1):
            title = getattr(track, "title", "Unknown Title")
            author = getattr(track, "author", "Unknown Author")
            description_text += f"**{i}.** {title}\n*by `{author}`*\n\n"
        
        embed = discord.Embed(
            title=f"{Emojis.book} Session History",
            description=description_text,
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Auro Engine • Only recent tracks are logged")
        
        if played_tracks and hasattr(played_tracks[0], "thumbnail"):
            embed.set_thumbnail(url=played_tracks[0].thumbnail)
        else:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(History(bot))