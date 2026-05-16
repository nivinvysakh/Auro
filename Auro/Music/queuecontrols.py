import discord
from discord.ext import commands
from typing import cast
from util.emojis import Emojis
from Auro.Music.play import Player
from discord import app_commands

class QueueControls(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="queue_clr",
        description="🗑️ Wipe all tracks from the current Auro Engine queue.",
        aliases=["qclear", "clearqueue", "qc"]
    )
    @commands.guild_only()
    async def clear(self,ctx:commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow())
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if player.queue.is_empty:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} **Queue is already empty.**",
                    color= discord.Color.yellow()
                )
            )
        track_count = len(player.queue)
        player.queue.clear()
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Queue Cleared",
                description=f"Successfully removed **{track_count}** tracks from the engine.",
                color= discord.Colour.green()
            ).set_footer(
               text="Auro Engine v1.0.0 • Queue Manager",
               icon_url=self.bot.user.avatar.url
            )
        )
    @commands.hybrid_command(
        name="queue_pop",
        aliases=["qpop", "undo"],
        description="💥 Remove the last track added to the Auro Engine queue."
    )
    @commands.guild_only()
    async def pop(self,ctx:commands.Context):
        player = cast(Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow())
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if player.queue.is_empty:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} **Queue is already empty.**",
                    color= discord.Color.yellow()
                )
            )
        removed_track = player.queue.pop()
        await ctx.reply(
            embed= discord.Embed(
            title=f"{Emojis.success} Track Removed",
            description=f"Successfully popped **{removed_track.title}** from the end of the queue.",
            color=discord.Color.orange()).set_footer(
               text="Auro Engine v1.0.0 • Queue Manager",
               icon_url=self.bot.user.avatar.url
            )
        )
    @commands.hybrid_command(
        name="queue_rmtrack",
        aliases=["qremove", "rm"],
        description="🎯 Remove a specific track from the queue by its name."
    )
    @app_commands.describe(
        target="🌛 The name (or part of the name) of the track you want to remove."
    )
    @commands.guild_only()
    async def remove(self,ctx: commands.Context , target : str):
        player = cast(Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow())
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if player.queue.is_empty:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} **Queue is already empty.**",
                    color= discord.Color.yellow()
                )
            )
        target_track = None
        for track in player.queue:
            if target.lower() in track.title.lower():
                target_track = track
                break
        if not target_track:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.warning} Could not find a track matching `{target}` in the queue.",
                    color=discord.Color.yellow()
                )
            )
        player.queue.remove(target_track)
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Track Removed",
                description=f"Successfully removed **{target_track.title}** from the engine.",
                color=discord.Color.red()
            ).set_footer(
               text="Auro Engine v1.0.0 • Queue Manager",
               icon_url=self.bot.user.avatar.url
            )
        )
    @commands.hybrid_command(
        name="queue_shuffle",
        aliases=["shuffle", "sh"],
        description="🔀 Randomize the order of tracks in the Auro Engine queue."
    )
    @commands.guild_only()
    async def shuffle(self,ctx:commands.Context):
        player = cast(Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow())
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if player.queue.is_empty:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} **Queue is already empty.**",
                    color= discord.Color.yellow()
                )
            )
        if len(player.queue) < 3 :
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Add at least **3 tracks** to the queue to shuffle.",
                    color= discord.Color.yellow()
                )
            )
        player.queue.shuffle()
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Queue Shuffled",
                description=f"Successfully randomized **{len(player.queue)}** tracks.",
                color=discord.Color.purple()
            )
        )
    @commands.hybrid_command(
        name="queue_move",
        description="🔄 Move a track to a specific position in the queue."
    )
    @app_commands.describe(
        current_pos="🌟 The current number of the song in the queue",
        target_pos="❇️ The number of the position you want to move it to"
    )
    @commands.guild_only()
    async def move(self,ctx:commands.Context, current_pos : int , target_pos : int):
        player = cast(Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow())
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if not player or current_pos < 1 or target_pos < 1 or current_pos > player.queue.size:
            return await ctx.reply(embed=discord.Embed(
                description=f"{Emojis.warning} Invalid position or the queue is empty.",
                color= discord.Color.yellow()
            ))
        track_list = list(player.queue)
        moved_track = track_list.pop(current_pos - 1)
        track_list.insert(target_pos - 1, moved_track)
        player.queue.clear()
        for track in track_list:
            player.queue.put(track)
        await ctx.reply(
            embed=discord.Embed(
                description=f"{Emojis.success} Moved **{moved_track.title}** to position `#{target_pos}`.",
                color= discord.Color.from_rgb(225,225,225)
            )
        )
        

async def setup(bot : commands.Bot):
    await bot.add_cog(QueueControls(bot))