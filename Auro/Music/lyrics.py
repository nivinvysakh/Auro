import discord
from discord.ext import commands
import syncedlyrics
import re
import asyncio
import requests
from Auro.Music.play import Player
from typing import cast
from util.emojis import Emojis
from anyascii import anyascii


class LyricsView(discord.ui.View):

    def __init__(self, raw_pages, transliterated_pages, track, bot, author):
        super().__init__(timeout=60)
        self.raw_pages = raw_pages
        self.transliterated_pages = transliterated_pages
        self.pages = raw_pages  
        self.is_translated = False  
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

        footer_text = f"Page {self.current_page + 1}/{len(self.pages)} • Auro Engine"
        if self.is_translated:
            footer_text += " • Note: Translations/Transliterations may not be fully accurate."

        embed.set_footer(
            text=footer_text,
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
        label="Translate", style=discord.ButtonStyle.secondary, emoji="🌐"
    )
    async def translate_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "This menu isn't for you! ┐(￣ヘ￣)┌", ephemeral=True
            )

        
        self.is_translated = not self.is_translated
        self.pages = self.transliterated_pages if self.is_translated else self.raw_pages
        
        
        button.style = discord.ButtonStyle.primary if self.is_translated else discord.ButtonStyle.secondary

        await interaction.response.edit_message(
            embed=self.create_embed(), view=self
        )

    @discord.ui.button(
        label="Locate", style=discord.ButtonStyle.blurple, emoji="🏹"
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
        label="delete", style=discord.ButtonStyle.danger, emoji=f"{Emojis.error}"
    )
    async def delete(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
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
            except Exception:
                pass


class Lyrics(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="lyrics", description="🎼 Get the lyrics of the currently playing song"
    )
    @commands.guild_only()
    async def lyrics(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)

        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color=discord.Color.yellow(),
                )
            )
        if not player.current:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Nothing is playing right now. Play a song first! `(￣ω￣;)`",
                    color=discord.Color.yellow(),
                )
            )
        if player.current.is_stream:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} `Lyrics` is not available for Radio",
                    color=discord.Color.yellow(),
                )
            )
        if (player.current.title).startswith("Auro"):
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} No Lyrics for Custom_play audio",
                    color=discord.Color.yellow(),
                )
            )
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()

        track = player.current
        search_query = f"{track.title} {track.author}"
        lrc_data = None
        
        try:
            lrc_data = await asyncio.to_thread(syncedlyrics.search, search_query)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            pass

        if not lrc_data:
            embed = discord.Embed(
                description=f"{Emojis.error} No synced lyrics found for **{track.title}**.",
                color=discord.Color.yellow(),
            )
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=6)

        lines = lrc_data.split("\n")
        current_pos_ms = player.position
        
        raw_lines = []
        transliterated_lines = []
        found_now_playing = False

        for line in lines:
            match = re.search(r"\[(\d+):(\d+\.?\d*)\](.*)", line)
            if not match:
                continue

            minutes, seconds, text = match.groups()
            text = text.strip()
            if not text:
                continue

            
            translated_text = anyascii(text)

            line_ms = (int(minutes) * 60 + float(seconds)) * 1000

            if not found_now_playing and line_ms >= current_pos_ms:
                raw_lines.append(f"**➜ {text}**")
                transliterated_lines.append(f"**➜ {translated_text}**")
                found_now_playing = True
            else:
                raw_lines.append(f"`[{minutes}:{seconds[:2]}]` {text}")
                transliterated_lines.append(f"`[{minutes}:{seconds[:2]}]` {translated_text}")

        raw_pages = [
            "\n".join(raw_lines[i : i + 10])
            for i in range(0, len(raw_lines), 10)
        ]
        transliterated_pages = [
            "\n".join(transliterated_lines[i : i + 10])
            for i in range(0, len(transliterated_lines), 10)
        ]

        if not raw_pages:
            return await ctx.send(f"{Emojis.error} No lyrics available for display.")

        view = LyricsView(raw_pages, transliterated_pages, track, self.bot, ctx.author)
        msg = await ctx.send(embed=view.create_embed(), view=view)
        view.message = msg


async def setup(bot: commands.Bot):
    await bot.add_cog(Lyrics(bot))