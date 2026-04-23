import discord
from discord.ext import commands
import pomice
from typing import cast
from discord import app_commands
from pomice.exceptions import FilterTagAlreadyInUse
from util.emojis import Emojis

class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="volume",
        description="🔊 Adjust the playback volume (0-100%)",
        aliases=["vol", "v", "volume_set", "setvolume"],
    )
    @commands.guild_only()
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, ctx: commands.Context, volume: int):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)

        if volume < 0 or volume > 100:
            return await ctx.reply(
                "❌ Volume must be between 0 and 100.", ephemeral=True
            )

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
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)

        filter_data = pomice.filters.Timescale.nightcore()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ Nightcore mode is already enabled.\n To reset the filters, use the `/reset` command.",
                ephemeral=True,
            )
        embed = discord.Embed(
            title=f"🌙 **Nightcore mode enabled!**", color=discord.Color.blurple()
        ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="vaporwave",
        description="💨 Slow down the track and lower the pitch",
        aliases=["vw", "vaporwave_mode", "enable_vaporwave"],
    )
    @commands.guild_only()
    async def vaporwave(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)

        filter_data = pomice.filters.Timescale.vaporwave()
        try:
            await player.add_filter(filter_data)
        except pomice.FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ Vaporwave mode is already enabled.\n To reset the filters, use the `/reset` command.",
                ephemeral=True,
            )
        embed = discord.Embed(
            title=f"💨 **Vaporwave mode enabled!**", color=discord.Color.blurple()
        ).set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eqbassboost",
        description="🔊 Boost the bass frequencies",
        aliases=["bb", "bass_boost", "enable_bassboost", "eqbass"],
    )
    @commands.guild_only()
    async def bassboost(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        try:
            filter_data = pomice.filters.Equalizer.boost()
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ Bassboost is already enabled. \n To reset the filters, use the `/reset` command.",
                ephemeral=True,
            )
        embed = (
            discord.Embed(
                title="Bassboost Enabled",
                description="🔊 Heavy bass frequencies have been boosted for maximum thump!",
                color=discord.Color.blurple(),
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eqflat",
        description="🎚️ Flatten the equalizer settings",
        aliases=["flat", "equalizer_flat", "enable_eqflat"],
    )
    @commands.guild_only()
    async def eqflat(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.flat()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ Flat equalizer settings are already enabled.\n To reset the filters, use the `/reset` command.",
                ephemeral=True,
            )
        embed = (
            discord.Embed(
                title="Equalizer Flattened",
                description="🎚️ All frequencies have been balanced to neutral settings.",
                color=discord.Color.blurple(),
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eqmetal",
        description="🎸 Enhance the mid frequencies for a metal sound",
        aliases=["metal", "equalizer_metal", "enable_eqmetal"],
    )
    @commands.guild_only()
    async def eqmetal(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.metal()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ Metal equalizer settings are already enabled.\n To reset the filters, use the `/reset` command.",
                ephemeral=True,
            )
        embed = (
            discord.Embed(
                title="Metal Equalizer Enabled",
                description="🎸 Mid frequencies enhanced for that aggressive metal sound!",
                color=discord.Color.blurple(),
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="eqpiano",
        description="🎹 Enhance the high frequencies for a piano sound",
        aliases=["piano", "equalizer_piano", "enable_eqpiano"],
    )
    @commands.guild_only()
    async def eqpiano(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)
        filter_data = pomice.filters.Equalizer.piano()
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ Piano equalizer settings are already enabled.\n To reset the filters, use the `/reset` command.",
                ephemeral=True,
            )
        embed = (
            discord.Embed(
                title="Piano Equalizer Enabled",
                description="🎹 High frequencies enhanced for crystal clear piano notes!",
                color=discord.Color.blurple(),
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
            .set_footer(text="💝", icon_url=self.bot.user.avatar.url)
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="8d",
        description="🔊 Enable 8D audio effect",
        aliases=["8d_audio", "enable_8d"],
    )
    @commands.guild_only()
    async def audio_8d(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ I'm not playing anything.", ephemeral=True)

        filter_data = pomice.filters.Rotation(tag="8d", rotation_hertz=0.2)
        try:
            await player.add_filter(filter_data)
        except FilterTagAlreadyInUse:
            return await ctx.reply(
                "❌ 8D audio effect is already enabled.", ephemeral=True
            )
        embed = (
            discord.Embed(
                title="8D Audio Effect Enabled",
                description="🔊 Immersive 3D spatial audio activated!",
                color=discord.Color.blurple(),
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
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
        player = cast(pomice.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(
                "⚠️ I'm not in a Voice Channel.", ephemeral=True
            )

        await interaction.response.defer()

        try:

            eq = pomice.Equalizer.flat()

            pairs = tuning.split()
            applied_bands = []

            for pair in pairs:
                if ":" not in pair:
                    continue
                b_str, g_str = pair.split(":", 1)
                band, gain = int(b_str), float(g_str)

                if 0 <= band <= 14:

                    clamped_gain = max(-0.25, min(1.0, gain))

                    eq.raw[band] = clamped_gain
                    applied_bands.append((band, clamped_gain))

            if not applied_bands:
                return await interaction.followup.send("❌ No valid bands found.")

            await player.add_filter(eq, fast_apply=True)

            embed = discord.Embed(
                title="🎚️ Auro Engine: Custom Tuning",
                description="\n".join([f"Band {b} → `{g}`" for b, g in applied_bands]),
                color=discord.Color.blurple(),
            )

            embed.set_footer(
                text="Auro Tuning System | Settings applied",
                icon_url=self.bot.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ **Auro Tuner Error:** `{e}`")

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
            name="eq_Treble_Boost",
            description="✨ Boost the high frequencies for extra sparkle",
            aliases=["treble_boost", "enable_treble_boost", "eqtreble","eq_tb"],
    )
    @commands.guild_only()
    async def eq_treble_boost(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)
        if not player :
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    color= discord.Color.red()
                ),
                delete_after=20
            )
        treble_boost_raw = [
            (0, -0.05),
            (1, -0.05),
            (2, -0.1),
            (3, 0.0),
            (4, 0.0),
            (5, 0.05),
            (6, 0.1),
            (7, 0.15),
            (8, 0.2),
            (9, 0.25),
            (10, 0.3),
            (11, 0.35),
            (12, 0.4),
            (13, 0.45),
            (14, 0.5)
        ]
        try:
            eq_filter = pomice.filters.Equalizer(tag="treble_boost", levels=treble_boost_raw)
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
                title=f"{Emojis.success} Treble Boost Enabled!",
                description="✨ High frequencies have been boosted for extra sparkle!",
                color= discord.Color.blurple()
            ).set_thumbnail(url=self.bot.user.avatar.url).set_footer(
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
        player = cast(pomice.Player, ctx.voice_client)
        if not player:
            return await ctx.reply("❌ No active player found.")

        await player.reset_filters(fast_apply=True)
        await ctx.reply("♻️ **All audio filters have been cleared.**")


async def setup(bot):
    await bot.add_cog(Filters(bot))
