import discord
from discord.ext import commands
from discord import app_commands
from Auro.Music.play import Player
from typing import cast
from util.emojis import Emojis

class SkipQueue(commands.Cog):
    def __init__(self , bot : commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="skipto",
        aliases=["st", "jumpto", "skiptopos"],
        description="⏩ Skip directly to a specific track position index inside the queue."
    )
    @commands.guild_only()
    @app_commands.describe(index="✨ The target track number position in the queue (e.g., 3, 5)")
    async def skipqueue(self, ctx : commands.Context , index : int):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} There is no active session running right now.",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in my channel!",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )
        if player.queue.is_empty:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} The queue is completely empty! Nothing to skip to.",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )

        queue_size = len(player.queue)
        if index < 1 or index > queue_size:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.error} Invalid position! Please choose a track number between `1` and `{queue_size}` (Check `a!queue`).",
                    color=discord.Color.red()
                ),
                delete_after=10
            )
        if queue_size < 3 :
            embed = discord.Embed(
                description=f"{Emojis.warning} The queue is too short! Use `a!skip` instead for small queues.",
                color= discord.Color.yellow()
            )
            return await ctx.reply(
                embed=embed,
                delete_after=15,
                ephemeral=True
            )
        
        tracks_to_remove = index - 1

        for _ in range(tracks_to_remove):
            skipped_track = player.queue.get()
            player.queue.put(skipped_track)
        
        target_track = player.queue.get()

        player.loop = False
        await player.music_cache.clear_all_guild_cache(ctx.guild.id)
        await player.play(target_track)

        embed = discord.Embed(
            description=f"{Emojis.success} **Skipped directly to position #{index}:** **{target_track.title}**",
            color=discord.Color.blurple()
        ).set_footer(text=f"Requested by {ctx.author.display_name}")

        await ctx.reply(embed=embed)
async def setup(bot : commands.Bot):
    await bot.add_cog(SkipQueue(bot))