import discord
import pomice
from discord.ext import commands
from typing import cast
from discord import app_commands
from Auro.Music.play import Player
from pomice.exceptions import FilterTagAlreadyInUse
from util.emojis import Emojis
from filters.eq_filters import Eq_Presets

class Filters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="volume",
        description="🔊 Adjust the playback volume (0-100%)",
        aliases=["vol", "v", "volume_set", "setvolume"],
    )
    @commands.guild_only()
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, ctx: commands.Context, volume: int):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        
        if volume < 0 or volume > 100:
            embed = discord.Embed(
                title=f"{Emojis.warning} Volume must be in between **0** and **100**",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)

        await player.set_volume(volume)
        embed = discord.Embed(
            title=f"🔊 **Volume set to `{volume}`%!", color=discord.Color.blurple()
        ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed, delete_after=20)

    @commands.hybrid_command(
        name="nightcore",
        description="🌙 Speed up the track and increase the pitch",
        aliases=["nc", "nightcore_mode", "enable_nightcore"],
    )
    @commands.guild_only()
    async def nightcore(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )

        filter_data = pomice.filters.Timescale.nightcore()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.warning} `nightcore` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
            description=f"🌙 **Nightcore mode enabled!**", color=discord.Color.blurple()
        ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="vaporwave",
        description="💨 Slow down the track and lower the pitch",
        aliases=["vw", "vaporwave_mode", "enable_vaporwave"],
    )
    @commands.guild_only()
    async def vaporwave(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )

        filter_data = pomice.filters.Timescale.vaporwave()
        try:
            await player.add_filter(filter_data)
        except pomice.FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.warning} `vaporwave` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Colour.yellow()
            )
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
            description=f"💨 **Vaporwave mode enabled!**", color=discord.Color.blurple()
        ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eq_bassboost",
        description="🔊 Boost the bass frequencies",
        aliases=["bb", "bass_boost", "enable_bassboost", "eqbass"],
    )
    @commands.guild_only()
    async def bassboost(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return ctx.reply(embed=embed)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        try:
            filter_data = pomice.filters.Equalizer.boost()
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.warning} `bassboost` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        embed = (
            discord.Embed(
                description=f"{Emojis.success} **Bassboost Enabled**",
                color=discord.Color.blurple(),
            )
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eq_flat",
        description="🎚️ Flatten the equalizer settings",
        aliases=["flat", "equalizer_flat", "enable_eqflat"],
    )
    @commands.guild_only()
    async def eqflat(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        filter_data = pomice.filters.Equalizer.flat()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.warning} `eqflat` is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
            )
            return ctx.reply(embed=embed)
        embed = (
            discord.Embed(
                description=f"{Emojis.success} Equalizer Flattened",
                color=discord.Color.blurple(),
            ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eq_metal",
        description="🎸 Enhance the mid frequencies for a metal sound",
        aliases=["metal", "equalizer_metal", "enable_eqmetal"],
    )
    @commands.guild_only()
    async def eqmetal(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return ctx.reply(embed=embed)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        filter_data = pomice.filters.Equalizer.metal()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.warning} `eqmetal` is active ",
                description= "`（；´д｀）ゞ`",
                color= discord.Color.yellow()
            )
            return ctx.reply(embed=embed)
        embed = (
            discord.Embed(
                description=f"{Emojis.success} Metal Equalizer Enabled",
                color=discord.Color.blurple(),
            )
            
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eq_piano",
        description="🎹 Enhance the high frequencies for a piano sound",
        aliases=["piano", "equalizer_piano", "enable_eqpiano"],
    )
    @commands.guild_only()
    async def eqpiano(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        filter_data = pomice.filters.Equalizer.piano()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.error} `Eqpiano` is active .",
                description="`（；´д｀）ゞ`",
                color= discord.Colour.yellow()
            )
            return ctx.reply(embed=embed)
        embed = (
            discord.Embed(
                description=f"{Emojis.success} Piano Equalizer Enabled",
                color=discord.Color.blurple(),
            ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="8d",
        description="🔊 Enable 8D audio effect",
        aliases=["8d_audio", "enable_8d"],
    )
    @commands.guild_only()
    @app_commands.describe(
        hz= "✨ Speed of the rotation (Suggested: 0.002 - 0.05)"
    )
    async def audio_8d(self, ctx: commands.Context, hz : float = 0.002):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if not (0.002 <= hz <= 0.05):
            embed = discord.Embed(
            description=f"{Emojis.warning} **Invalid Range:** Speed must be between `0.002` and `0.05` Hz.",
            color=discord.Color.yellow()
            )
            return await ctx.reply(embed=embed, ephemeral=True)

        filter_data = pomice.filters.Rotation(tag="8d", rotation_hertz=hz)
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            embed = discord.Embed(
                title=f"{Emojis.warning} `8d` filter is active.",
                description="`（；´д｀）ゞ`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        embed = (
            discord.Embed(
                description=f"{Emojis.success} 8D Audio Effect Enabled",
                color=discord.Color.blurple(),
            )
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @app_commands.command(
        name="seteq",
        description="🎛️ Manually tune the Auro Engine frequency bands",
    )
    @app_commands.guild_only()
    @app_commands.describe(tuning="Format: 'band:gain' (e.g., '0:0.25 1:0.15')")
    async def seteq(self, interaction: discord.Interaction, tuning: str):
        player = cast(Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(
                f"{Emojis.warning} I'm not in a Voice Channel.", ephemeral=True
            )
        if not interaction.user.voice or interaction.user.voice.channel != player.channel:
            return await interaction.response.send_message(
                f"╮(￣ω￣;)╭ You're not in {player.channel.mention}!", ephemeral=True
            )
        await interaction.response.defer()

        try:
            pairs = tuning.split()
            filter_data = []

            for pair in pairs:
                if ":" not in pair:
                    continue
                b_str, g_str = pair.split(":", 1)
                band, gain = int(b_str), float(g_str)

                if 0 <= band <= 14:

                    clamped_gain = max(-0.25, min(1.0, gain))
                    filter_data.append((band, clamped_gain))

            if not filter_data:
                return await interaction.followup.send("❌ No valid bands found.")
            eq = pomice.Equalizer(levels=filter_data, tag="Custom_Eq")
            await player.add_filter(eq, fast_apply=True)

            embed = discord.Embed(
                title="🎚️ Auro Engine: Custom Tuning",
                description="\n".join([f"Band {b} → `{g}`" for b, g in filter_data]),
                color=discord.Color.blurple(),
            )
            embed.set_thumbnail(url=player.current.thumbnail)
            embed.set_footer(
                text="Auro Tuning System | Settings applied",
                icon_url=self.bot.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except FilterTagAlreadyInUse:
            return await interaction.followup.send(embed=discord.Embed(
                title=f"{Emojis.warning} Custom Tune  is already in use.",
                description="To reset the filters run `/reset` command.",
                color= discord.Color.yellow()
            ))

    @app_commands.command(
        name="eq_help",
        description="💞 Guide for the Auro Engine frequency bands",
    )
    async def eq_help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎚️ Auro Engine: Frequency Guide",
            description=(
                "Auro uses a **15-band Equalizer** (Bands 0-14).\n"
                "Adjust bands using `/seteq tuning: band:gain`"
            ),
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="低 Sub-Bass & Bass (0 - 3)",
            value="Controls the 'Thump' and 'Punch'.\n*Recommended: 0.15 to 0.30*",
            inline=False,
        )
        embed.add_field(
            name="🎸 Low-Mids & Mids (4 - 9)",
            value="Controls Vocals and Instruments.\n*Recommended: -0.10 to 0.10*",
            inline=False,
        )
        embed.add_field(
            name="✨ Highs & Treble (10 - 14)",
            value="Controls Clarity and Cymbals.\n*Recommended: 0.10 to 0.25*",
            inline=False,
        )

        embed.add_field(
            name="📝 Example Tuning",
            value="`/seteq tuning: 0:0.25 1:0.20 14:0.25`",
            inline=False,
        )

        embed.set_footer(
            text="Range: -0.25 (Min) to 1.0 (Max)",
            icon_url=self.bot.user.display_avatar.url,
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
    @commands.hybrid_command(
            name="eq_treble_boost",
            description="✨ Boost the high frequencies for extra sparkle",
            aliases=["treble_boost", "enable_treble_boost", "eqtreble","eq_tb"],
    )
    @commands.guild_only()
    async def eq_treble_boost(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player :
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()

                ),
                delete_after=20
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        
        try:
            eq_filter = pomice.filters.Equalizer(tag="treble_boost", levels=Eq_Presets.TREBLE_BOOST)
            await player.add_filter(
                eq_filter,fast_apply=True
            )
        except FilterTagAlreadyInUse :
            return await ctx.reply(
                embed= discord.Embed(
                    title=f"{Emojis.warning} Treble_boost is already in use.",
                    description="To reset the filters run `/reset` command.",
                    color= discord.Color.yellow()
                ),
                delete_after=15
            )
        await ctx.reply(
            embed= discord.Embed(
                description=f"{Emojis.success} Treble Boost Enabled!",
                color= discord.Color.blurple()
            ).set_footer(
                text="💝", icon_url=self.bot.user.avatar.url
            )
        )
    @commands.hybrid_command(
        name="reset",
        description="♻️ Clear all audio filters",
        aliases=["reset_filters", "clear_filters", "remove_filters"],
    )
    @commands.guild_only()
    async def reset_filters(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            embed = discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )

        await player.reset_filters(fast_apply=True)
        embed = discord.Embed(
            description=f"{Emojis.success} **All audio filters have been cleared.**",
            color= discord.Color.blurple()
        ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)


async def setup(bot : commands.Bot):
    await bot.add_cog(Filters(bot))
