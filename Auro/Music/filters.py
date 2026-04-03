from discord.ext import commands
import pomice
from typing import cast
from discord import app_commands
class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_command(name="volume", description="🔊 Adjust the playback volume (0-100%)")
    @commands.guild_only()
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, ctx: commands.Context, volume: int):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)

        if volume < 0 or volume > 100:
            return await ctx.reply("❌ Volume must be between 0 and 100.", ephemeral=True)

        await player.set_volume(volume)
        await ctx.reply(f"🔊 **Volume set to {volume}%!**")
    
    @commands.hybrid_command(name="nightcore", description="🌙 Speed up the track and increase the pitch")
    @commands.guild_only()
    async def nightcore(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)

        filter_data = pomice.filters.Timescale.nightcore()
        await player.add_filter(filter_data)
        
        await ctx.reply("🌙 **Nightcore mode enabled!**")

    @commands.hybrid_command(name="vaporwave",description="💨 Slow down the track and lower the pitch")
    @commands.guild_only()
    async def vaporwave(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        
        filter_data = pomice.filters.Timescale.vaporwave()
        await player.add_filter(filter_data)
        await ctx.reply("💨 **Vaporwave mode enabled!**")

    @commands.hybrid_command(name="eqbassboost", description="🔊 Boost the bass frequencies")
    @commands.guild_only()
    async def bassboost(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.boost()
        await player.add_filter(filter_data)
        await ctx.reply("🔊 **Bassboost enabled!**")
    
    @commands.hybrid_command(name="eqflat",description="🎚️ Flatten the equalizer settings")
    @commands.guild_only()
    async def eqflat(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.flat()
        await player.add_filter(filter_data)
        await ctx.reply("🎚️ **Equalizer settings flattened!**")
    
    @commands.hybrid_command(name="eqmetal",description="🎸 Enhance the mid frequencies for a metal sound")
    @commands.guild_only()
    async def eqmetal(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.metal()
        await player.add_filter(filter_data)
        await ctx.reply("🎸 **Metal equalizer enabled!**")
    
    @commands.hybrid_command(name="eqpiano",description="🎹 Enhance the high frequencies for a piano sound")
    @commands.guild_only()
    async def eqpiano(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.piano()
        await player.add_filter(filter_data)
        await ctx.reply("🎹 **Piano equalizer enabled!**")
    
    @commands.hybrid_command(name="8d", description="🔊 Enable 8D audio effect")
    @commands.guild_only()
    async def audio_8d(self,ctx:commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        
        filter_data = pomice.filters.Rotation(tag="8d",rotation_hertz=0.2)
        await player.add_filter(filter_data)
        await ctx.reply("🔊 **8D audio effect enabled!**")

    @commands.hybrid_command(name="reset", description="♻️ Clear all audio filters")
    @commands.guild_only()
    async def reset_filters(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ No active player found.")

        await player.reset_filters()
        await ctx.reply("♻️ **All audio filters have been cleared.**")

async def setup(bot):
    await bot.add_cog(Filters(bot))