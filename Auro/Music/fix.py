import discord
import pomice
from discord.ext import commands
import asyncio
from typing import cast
from util.emojis import Emojis
from .play import Player

class Fix(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="fix",
        description="🍋 Hard-resets the Auro Engine to fix 'Ghost Audio' issues.",
        aliases=["reset_player","hard_reset"]
    )
    @commands.guild_only()
    @commands.cooldown(3,120, commands.BucketType.guild)
    async def fix(self,ctx:commands.Context):
        player = cast(Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color= discord.Colour.yellow()
                ),delete_after=20
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color= discord.Color.yellow()
                ),delete_after=20
            )
        warning_msg = ""
        if player.loop or player.loop_queue:
            warning_msg += f"\n{Emojis.dot} **Looping/Queue Loop** will be disabled."
        if not player.queue.is_empty:
            warning_msg += f"\n{Emojis.dot} **Current Queue** ({len(player.queue)} songs) will be cleared."
        msg = await ctx.reply(
            embed= discord.Embed(
                description=f"Resetting the UDP stream to clear ghost audio.{warning_msg}\n\n*Proceeding with recovery...*",
                color=discord.Color.orange()
            )
        )
        await asyncio.sleep(5)
        current_track = player.current
        position = player.position
        vc_channel = player.channel
        try:
            await player.music_cache.clear_guild_cache(ctx.guild.id)
            await player.music_cache.clear_loop_queue(ctx.guild.id)
            await player.channel.edit(status=None)
            await player.destroy()
            await asyncio.sleep(2)
            new_player = cast(Player, await vc_channel.connect(cls=Player))
            new_player.controller = ctx.channel
            new_player.loop = False
            new_player.loop_queue = False
            if current_track:
                await new_player.channel.edit(status=f"{Emojis.auro} Auro Music !")
                await new_player.play(current_track, start=position)
        except Exception as e :
            print(f"Fix command error : {e}")
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} ⚠️ **Recovery Failed** . Please Contact the devs so that they can fully reset the system.",
                    color= discord.Color.red()
                ),delete_after=20
            )
        else:
            if not current_track:
                await msg.edit(
                    embed=discord.Embed(
                        description=f"{Emojis.success} **Auro Engine:** Audio path restored.",
                        color=discord.Color.green()
                    )
                )
            else:
                await msg.edit(
                    embed=discord.Embed(
                    description=f"{Emojis.success} **Auro Engine:** Audio path restored. Playback resumed. ",
                    color=discord.Color.gold()
                ),delete_after=20
                )

async def setup(bot : commands.Bot):
    await bot.add_cog(Fix(bot))
