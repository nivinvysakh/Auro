import discord
from discord.ext import commands
from util.emojis import Emojis
from Auro.Music.play import Player
from typing import cast
class Save(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="save",
        description="📩 Sends the current song details to your DMs."
    )
    @commands.guild_only()
    async def save(self,ctx:commands.Context):
        player = cast(Player,ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed,delete_after=10)
        if not player.current:
            embed = discord.Embed(
                title=f"{Emojis.error} Nothing is playing right now!",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed,delete_after=10)
        track = player.current
        thumbnail = getattr(track, "thumbnail", self.bot.user.avatar.url)
        embed = discord.Embed(
            title=f"{Emojis.star_animate} Saved Track: {track.title}",
            description=(
                f"**Author:** `{track.author}`\n"
                f"**Source:** [Click here to listen]({track.uri})\n\n"
                f"*Saved from {ctx.guild.name}*"
            ),
            color= discord.Color.green()
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text="Auro Engine • Save", icon_url=self.bot.user.avatar.url)
        try :
            msg = await ctx.author.send(embed=embed)
            await msg.add_reaction("❤️‍🩹")
            await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.success} I've sent the details to your DMs, {ctx.author.mention}!",
                ) , delete_after=10
            )
        except discord.Forbidden:
            await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} {ctx.author.mention}, I couldn't DM you! Please check your privacy settings.",
                    color= discord.Color.yellow()
                )
            )
async def setup(bot : commands.Bot):
    await bot.add_cog(Save(bot))