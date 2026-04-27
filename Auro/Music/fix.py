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
        description="🍋‍🟩 Hard-resets the Auro Engine to fix 'Ghost Audio' issues.",
        aliases=["reset_player","hard_reset"]
    )
    @commands.guild_only()
    @commands.cooldown(3,120, commands.BucketType.guild)
    async def fix(self,ctx:commands.Context):
        player = cast(pomice.Player,ctx.voice_client)
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
        
        msg = await ctx.reply(
            embed= discord.Embed(
                description=f"{Emojis.success} **Auro Engine:** Resetting UDP stream...",
                color=discord.Color.green()
            )
        )
        current_track = player.current
        position = player.position
        vc_channel = player.channel
        try:
            await player.destroy()
            await asyncio.sleep(2)
            new_player = cast(pomice.Player, await vc_channel.connect(cls=Player))
            if current_track:
                await new_player.play(current_track, start=position)
        except Exception as e :
            print(e)
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

async def setup(bot):
    await bot.add_cog(Fix(bot))
