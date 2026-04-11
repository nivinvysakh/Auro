import discord
from discord.ext import commands
import pomice
import syncedlyrics
import re
from typing import cast
from util.emojis import Emojis
from discord import app_commands


class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_time(self, ms: int) -> str:

        seconds = int((ms / 1000) % 60)
        minutes = int((ms / (1000 * 60)) % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def parse_time(self, time_str: str) -> int:
        try:
            if ":" in time_str:
                parts = time_str.split(":")

                if len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    total_seconds = (minutes * 60) + seconds
                elif len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    total_seconds = (hours * 3600) + (minutes * 60) + seconds
            else:
                total_seconds = int(time_str)

            return total_seconds * 1000
        except ValueError:
            return -1

    @commands.hybrid_command(
        name="lyrics", description="Get the lyrics of the currently playing song"
    )
    @commands.guild_only()
    async def lyrics(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)

        if not player or not player.is_playing:
            return await ctx.reply(f"{Emojis.error} No music is currently playing.")

        await ctx.defer()

        track = player.current
        search_query = f"{track.title} {track.author}"

        lrc_data = syncedlyrics.search(search_query)

        if not lrc_data:
            return await ctx.send(
                f"{Emojis.error} No synced lyrics found for **{track.title}**."
            )

        lines = lrc_data.split("\n")
        current_pos_ms = player.position

        processed_lyrics = []
        current_line_text = "..."

        for line in lines:
            match = re.search(r"\[(\d+):(\d+\.?\d*)\](.*)", line)
            if not match:
                continue

            minutes, seconds, text = match.groups()
            text = text.strip()
            if not text:
                continue

            line_ms = (int(minutes) * 60 + float(seconds)) * 1000

            if line_ms <= current_pos_ms:
                current_line_text = f"**➜ {text}**"
            else:
                processed_lyrics.append(f"`[{minutes}:{seconds[:2]}]` {text}")

        upcoming_display = "\n".join(processed_lyrics[:7])

        embed = discord.Embed(
            title=f"Lyrics | {track.title}",
            description=f"** {Emojis.musicplaying} Now Playing:**\n{current_line_text}\n\n**Upcoming:**\n{upcoming_display or '*End of track*'}",
            color=discord.Color.blurple(),
        )

        embed.set_thumbnail(url=track.thumbnail)
        embed.set_footer(
            text=f"Auro Engine • {self.format_time(current_pos_ms)} / {self.format_time(track.length)}",
            icon_url=self.bot.user.display_avatar.url,
        )

        await ctx.send(embed=embed, delete_after=30)

    @commands.hybrid_command(
        name="seek", description="Jump to a specific time in the song"
    )
    @commands.guild_only()
    @app_commands.describe(time="Time to seek to (mm:ss or hh:mm:ss)")
    async def seek(self, ctx: commands.Context, time: str):
        player = cast(pomice.Player, ctx.voice_client)

        if not player or not player.is_playing:
            return await ctx.reply(f"{Emojis.error} No music is currently playing.")

        seek_ms = self.parse_time(time)

        if seek_ms < 0:
            return await ctx.reply(
                f"{Emojis.error} Invalid time format. Use `mm:ss` or `hh:mm:ss`."
            )
        if seek_ms > player.current.length:
            return await ctx.reply(f"{Emojis.error} Time exceeds track length.")

        await player.seek(seek_ms)

        await ctx.reply(
            f"{Emojis.success} Seeked to {self.format_time(seek_ms)}.", delete_after=5
        )


async def setup(bot):
    await bot.add_cog(Lyrics(bot))
