import discord
from discord.ext import commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class History(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.hybrid_command(
        name="history",
        description="📜 View the last 10 tracks played in this session.",
        aliases=["his"]
    )
    @commands.guild_only()
    async def history(self,ctx:commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color=discord.Color.yellow()
            )
            return await ctx.reply(embed=embed, delete_after=10)
        player = cast(Player, ctx.voice_client)
        if not player.history:
            embed = discord.Embed(
                title=f"{Emojis.warning} The history is currently empty!",
                description="`(￣ω￣;)`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed , delete_after=10)
        
        history_list = list(player.history)
        history_list.reverse()
        description_text = ""
        for i ,track_info in enumerate(history_list,1):
           description_text += f"**{i}.** {track_info}\n"
        
        embed = discord.Embed(
            title=f"{Emojis.book} Session History",
            description=description_text,
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Auro Engine • Only recent tracks are logged")
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.reply(
            embed=embed
        )
async def setup(bot):
    await bot.add_cog(History(bot))