import discord
from discord.ext import commands
import pomice
import syncedlyrics
import re
import asyncio
from typing import cast
from util.emojis import Emojis
from discord import app_commands


class LyricsView(discord.ui.View):

    def __init__(self,pages, track, bot,author):
        super().__init__(timeout=60)
        self.pages = pages
        self.current_page = 0
        self.track = track
        self.bot = bot
        self.message = None
        self.author = author

    def create_embed(self):
        embed = discord.Embed(
            title=f"Lyrics | {self.track.title}",
            description=self.pages[self.current_page],
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url=self.track.thumbnail)
        embed.set_footer(
            text=f"Page {self.current_page + 1}/{len(self.pages)} • Auro Engine",
            icon_url=self.bot.user.display_avatar.url,
        )
        return embed

    @discord.ui.button(
        label="Back", style=discord.ButtonStyle.gray, emoji=Emojis.left_arrow
    )
    async def back_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "This menu isn't for you! ┐(￣ヘ￣)┌", ephemeral=True
            )

        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.create_embed(), view=self
            )
        else:
            await interaction.response.defer()

    @discord.ui.button(
        label="Next", style=discord.ButtonStyle.gray, emoji=Emojis.right_arrow
    )
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "This menu isn't for you! ┐(￣ヘ￣)┌", ephemeral=True
            )
        
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.create_embed(), view=self
            )
        else:
            await interaction.response.defer()
    @discord.ui.button(
            label="Locate" , style=discord.ButtonStyle.blurple , emoji="🏹"
    )
    async def locator_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "This menu isn't for you! ┐(￣ヘ￣)┌", ephemeral=True
            )
        found_page = 0
        for index, content in enumerate(self.pages):
            if "➜" in content:
                found_page = index
                break
        self.current_page = found_page
        await interaction.response.edit_message(
            embed=self.create_embed(), view=self
        )
    @discord.ui.button(
            label="delete",
            style=discord.ButtonStyle.danger,
            emoji=f"{Emojis.error}"
    )
    async def delete(self, interaction : discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "This menu isn't for you! ┐(￣ヘ￣)┌", ephemeral=True
            )
        await interaction.message.delete()
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass


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
        name="lyrics", description="🎼 Get the lyrics of the currently playing song"
    )
    @commands.guild_only()
    async def lyrics(self, ctx: commands.Context):
        player = cast(pomice.Player, ctx.voice_client)

        if not player :
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
                )
            )
        if not player.current:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Nothing is playing right now. Play a song first! `(￣ω￣;)`",
                    color=discord.Color.yellow()
                )
            )
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        track = player.current
        search_query = f"{track.title} {track.author}"
        lrc_data = await asyncio.to_thread(syncedlyrics.search, search_query)

        if not lrc_data:
            return await ctx.send(
                f"{Emojis.error} No synced lyrics found for **{track.title}**."
            )

        lines = lrc_data.split("\n")
        current_pos_ms = player.position
        processed_lines = []
        found_now_playing = False

        for line in lines:
            match = re.search(r"\[(\d+):(\d+\.?\d*)\](.*)", line)
            if not match:
                continue

            minutes, seconds, text = match.groups()
            text = text.strip()
            if not text:
                continue

            line_ms = (int(minutes) * 60 + float(seconds)) * 1000

            if not found_now_playing and line_ms >= current_pos_ms:
                processed_lines.append(f"**➜ {text}**")
                found_now_playing = True
            else:
                processed_lines.append(f"`[{minutes}:{seconds[:2]}]` {text}")

        pages = [
            "\n".join(processed_lines[i : i + 10])
            for i in range(0, len(processed_lines), 10)
        ]

        if not pages:
            return await ctx.send(f"{Emojis.error} No lyrics available for display.")

        view = LyricsView(pages, track, self.bot,ctx.author)
        msg = await ctx.send(embed=view.create_embed(), view=view)
        view.message = msg

    @commands.hybrid_command(
        name="seek", description="🌊 Jump to a specific time in the song"
    )
    @commands.guild_only()
    @app_commands.describe(time="✨ Time to seek to (mm:ss or hh:mm:ss)")
    async def seek(self, ctx: commands.Context, time: str):
        player = cast(pomice.Player, ctx.voice_client)

        if not player :
            return await ctx.reply(
                embed=discord.Embed(
                title=f"{Emojis.error} No active player found.",
                description="`＞︿＜`",
                color= discord.Color.yellow()
                )
            )
        if not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Nothing is playing right now. Play a song first! `(￣ω￣;)`",
                    color=discord.Color.yellow()
                )
            )
        
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )

        seek_ms = self.parse_time(time)

        if seek_ms < 0:
            return await ctx.reply(
                f"{Emojis.error} Invalid format. Use `mm:ss` or `hh:mm:ss`."
            )
        if seek_ms > player.current.length:
            return await ctx.reply(
                embed= discord.Embed(
                    description=f"{Emojis.warning} Track limit exceeded.",
                    color= discord.Color.yellow()
                )
            )

        await player.seek(seek_ms)
        await ctx.reply(
            embed= discord.Embed(
                description=f"{Emojis.success} Seeked to {self.format_time(seek_ms)}.",
                color= discord.Color.green()
            ).set_author(name="Auro", icon_url=self.bot.user.avatar.url).set_thumbnail(url=player.current.thumbnail),delete_after=15
        )


async def setup(bot):
    await bot.add_cog(Lyrics(bot))
