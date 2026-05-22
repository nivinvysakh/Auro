import discord
from discord.ext import commands
from discord import app_commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class FindTrack(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="find",
        aliases=["searchqueue", "trackpos", "whereis"],
        description="🔍 Find the position number of a specific song inside the upcoming queue."
    )
    @commands.guild_only()
    @app_commands.describe(name="✨ The name or partial name of the song you want to find")
    async def find(self, ctx: commands.Context, *, name: str):
        player = cast(Player, ctx.voice_client)
        
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} No active player session found.",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )

        if player.queue.is_empty:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} The queue is completely empty! Nothing to search through.",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )

        search_query = name.lower().strip()

        if player.current and search_query in player.current.title.lower():
            embed = discord.Embed(
                title=f"{Emojis.musicplaying} Track is Playing Now",
                description=f"The song **{player.current.title}** is currently playing right now!",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Auro Engine • Active Track")
            if hasattr(player.current, "thumbnail"):
                embed.set_thumbnail(url=player.current.thumbnail)
            return await ctx.reply(embed=embed)
        

        found_position = None
        matched_track = None

        for index, track in enumerate(list(player.queue), 1):
            if search_query in track.title.lower():
                found_position = index
                matched_track = track
                break  

        if found_position is None:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"🔍 Couldn't find any song matching `{name}` inside the upcoming queue.",
                    color=discord.Color.red()
                )
            )

        embed = discord.Embed(
            title="🔍 Track Position Found",
            description=f"The song **{matched_track.title}** is currently sitting at position **#{found_position}** in the queue.",
            color=discord.Color.blurple()
        )
        
        songs_ahead = found_position - 1
        if songs_ahead == 0:
            embed.set_footer(text=f"Auro Engine • This song is playing NEXT!")
        else:
            embed.set_footer(text=f"Auro Engine • There are {songs_ahead} songs playing ahead of this one.")

        if hasattr(matched_track, "thumbnail"):
            embed.set_thumbnail(url=matched_track.thumbnail)

        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(FindTrack(bot))