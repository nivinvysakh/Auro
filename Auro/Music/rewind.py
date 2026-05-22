import discord
from discord.ext import commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class Rewind(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="rewind",
        aliases=["previous", "prev", "back"],
        description="⏪ Replay the track that just finished playing."
    )
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rewind(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} I am not active in a voice channel right now.",
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

        if player.is_playing:
            if len(player.history) < 2:
                return await ctx.reply(
                    embed=discord.Embed(
                        description=f"{Emojis.warning} No previous track found in Auro's history cache!",
                        color=discord.Color.yellow()
                    ),
                    delete_after=10
                )
            current_playing_track = player.history.pop()  
            previous_track = player.history.pop()         
            player.queue.put_at_front(current_playing_track)
        else:
            if len(player.history) < 1:
                return await ctx.reply(
                    embed=discord.Embed(
                        description=f"{Emojis.warning} No previous track found in Auro's history cache!",
                        color=discord.Color.yellow()
                    ),
                    delete_after=10
                )
            previous_track = player.history.pop()

        player.loop = False
        await player.music_cache.clear_guild_cache(ctx.guild.id)

        await player.play(previous_track)

        embed = discord.Embed(
            description=f"⏪ **Rewinding playback to:** **{previous_track.title}**",
            color=discord.Color.blurple()
        ).set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rewind(bot))