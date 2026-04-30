import pomice
import discord
from typing import cast
from util.emojis import Emojis
from pomice.exceptions import FilterTagAlreadyInUse
from discord.ext  import commands
from filters.eq_filters import Eq_Presets
from discord import app_commands
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
                embed = discord.Embed(
                title=f"{Emojis.warning} `eq dynamic` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
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
                embed = discord.Embed(
                title=f"{Emojis.warning} `eq smooth` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
            ))
        await ctx.reply(
            embed= discord.Embed(
                description="🌙 **Smooth EQ Active**",
                color= discord.Color.blurple()
            )
        )
    @commands.hybrid_command(
        name="vibrato",
        description="🌊 Wavy Effect: Adds a rhythmic pitch pulsation for a trippy, underwater sound"
    )
    @commands.guild_only()
    @app_commands.describe(
        frequency="😵‍💫 How fast it wobbles (0.1 to 14.0)",
        depth="🌛 How hard the pitch shifts (0.0 to 1.0)"
    )
    async def vibrato(self,ctx:commands.Context,frequency: float = 2.0, depth: float = 0.5):
        player = cast(pomice.Player,ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color= discord.Color.yellow()
                )
            )
        if not ctx.author.voice or  ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color= discord.Colour.yellow()
                )                
            )
        if not (0.1 <= frequency <= 14.0) or not (0.0 <= depth <= 1.0):
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Keep frequency between 0.1-14 and depth between 0.0-1.0!",
                    color= discord.Color.yellow()
                )
            )
        try :
            await player.add_filter(pomice.filters.Vibrato(tag="vibrato",frequency=frequency,depth=depth))
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                embed = discord.Embed(
                title=f"{Emojis.warning} `Vibrato` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
                )
            )
        msg = "🌊 **Wavy Mode: ON**" if depth < 0.8 else "😵‍💫 **MEME MODE: MAX WOBBLE**"
        await ctx.reply(
            embed=discord.Embed(
                title=msg,
                description=f"Frequency: `{frequency}Hz` | Depth: `{depth}`",
                color= discord.Color.green() if depth < 0.8 else discord.Color.gold()
            )
        )        

async def setup(bot):
    await bot.add_cog(Filter2(bot))