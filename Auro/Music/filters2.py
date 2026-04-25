import pomice
import discord
from typing import cast
from util.emojis import Emojis
from pomice.exceptions import FilterTagAlreadyInUse
from discord.ext  import commands
from presets import Eq_Presets

class Filter2(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="eq_dynamic",
        description="🥁 Balanced punch and sparkle",
    )
    @commands.guild_only()
    async def eq_dynamic(self,ctx:commands.Context):
        player = cast(pomice.Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed= discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color= discord.Color.yellow()
                )
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed= discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color= discord.Color.yellow()
                )
            )
        
        try:
            await player.add_filter(
                pomice.Equalizer(
                    tag="dynamic",
                    levels= Eq_Presets.DYNAMIC
                )
            )
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                embed= discord.Embed(
                    description=f"{Emojis.warning} `Dynamic` is active.",
                    color= discord.Colour.yellow()
                )
            )
        await ctx.reply(
            embed=discord.Embed(
                description=f"{Emojis.success} **Dynamic EQ Enabled!**",
                color= discord.Color.blurple()
            )
        )
    @commands.hybrid_command(
        name="eq_smooth",
        description="🌙 Warm & relaxed: Reduces sharp treble for late-night vibes"
    )
    @commands.guild_only()
    async def eq_smooth(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color= discord.Colour.yellow()
                )
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color= discord.Colour.yellow()
                )
            )
        try:
            await player.add_filter(
                pomice.Equalizer(
                    tag="smooth",
                    levels=Eq_Presets.SMOOTH
                )
            )
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                embed=discord.Embed(
                   description=f"{Emojis.warning} `smooth` is active.",
                   color= discord.Color.yellow() 
                )
            )
        await ctx.reply(
            embed= discord.Embed(
                description="🌙 **Smooth EQ Active**",
                color= discord.Color.blurple()
            )
        )

async def setup(bot):
    await bot.add_cog(Filter2(bot))