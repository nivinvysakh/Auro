import discord
from discord.ext import commands
from typing import Optional
from util.emojis import Emojis

class StatusPlay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="playfromstatus", 
        aliases=["pfs"],
        description="🎷 Play the music from your status or a friend's Spotify."
    )
    @commands.guild_only()
    @discord.app_commands.describe(member="✨ The user whose Spotify you want to sync from")
    async def playfromstatus(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        raw_target = member or ctx.author
        
        if raw_target.bot:
            embed = discord.Embed(
                description=f"{Emojis.warning} I can't sync music from bots!",
                color=discord.Color.yellow()
            )
            return await ctx.send(embed=embed, ephemeral=True, delete_after=10)

        target = ctx.guild.get_member(raw_target.id) or raw_target
        target_song = None
        
        if target.activities:
            for activity in target.activities:
                if isinstance(activity, discord.Spotify):
                    target_song = f"{activity.title} {activity.artist}"
                    break

        if not target_song:
            who = "You don't" if target == ctx.author else f"**{target.display_name}** doesn't"
            embed = discord.Embed(
                description=f"{Emojis.warning} {who} have an active **Spotify** status!",
                color=discord.Color.yellow()
            )
            return await ctx.send(embed=embed, delete_after=10, ephemeral=True)

        music_cog = self.bot.get_cog("Music")
        if music_cog:
            await ctx.invoke(music_cog.play, search=target_song)
        else:
            embed = discord.Embed(
                description=f"{Emojis.error} Music Engine not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatusPlay(bot))