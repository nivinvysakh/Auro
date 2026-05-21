import discord
from discord.ext import commands
from typing import Optional, cast
from discord import app_commands
import asyncio
import pomice
import json
import re
from util.emojis import Emojis
from Auro.Music.play import Player
from databases import MusicStorage

class PlaylistPagination(discord.ui.View):
    def __init__(self, author: discord.User, playlist_name: str, tracks: list):
        super().__init__(timeout=60)
        self.author = author
        self.playlist_name = playlist_name
        self.tracks = tracks
        self.current_page = 0
        self.per_page = 5
        self.max_pages = (len(tracks) - 1) // self.per_page + 1
        self.message: Optional[discord.Message] = None

    def get_page_embed(self) -> discord.Embed:
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_tracks = self.tracks[start:end]

        embed = discord.Embed(
            title=f"📂 Playlist: {self.playlist_name.title()}",
            color=discord.Color.blurple()
        )
        
        description = ""
        for index, (_, track_title) in enumerate(page_tracks, start=start + 1):
            description += f"`{index:02d}.` **{track_title}**\n"
            
        embed.description = description or "*This playlist is currently empty.*"
        embed.set_footer(text=f"Page {self.current_page + 1} of {self.max_pages} | Total Tracks: {len(self.tracks)}")
        return embed

    def update_buttons(self):
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page >= self.max_pages - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"{Emojis.warning} This menu isn't for you!",
                    color=discord.Color.yellow()
                ), ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        try:
            if self.message:
                await self.message.edit(view=self)
        except Exception:
            pass

    @discord.ui.button(label="Previous", emoji="◀️", style=discord.ButtonStyle.secondary, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Next", emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)


class CustomPlaylists(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MusicStorage()

    @commands.hybrid_group(
        name="myplaylist", 
        description="📂 Manage your personal saved playlists."
    )
    @commands.guild_only()
    async def myplaylist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                description=f"{Emojis.warning} **Invalid usage!** Try using these commands instead:\n"
                            f"➡️ `/myplaylist save` • `/myplaylist load` • `/myplaylist view` • `/myplaylist list` • `/myplaylist delete`",
                color=discord.Color.yellow()
            )
            await ctx.reply(embed=embed, delete_after=7)

    @myplaylist.command(
        name="save", 
        description="💾 Save the currently playing song to a personal playlist."
    )
    @app_commands.describe(playlist_name="✨ Choose a name for your playlist")
    async def save_track(self, ctx: commands.Context, playlist_name: str):
        if not ctx.author.voice:
            embed = discord.Embed(description=f"{Emojis.warning} You must be in a voice channel to save music!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)
        
        player = cast(Player, ctx.voice_client)
        if not player or not player.current:
            embed = discord.Embed(description=f"{Emojis.warning} There is nothing playing right now to save!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)
            
        if player.current.is_stream:
            embed = discord.Embed(description=f"{Emojis.warning} Live radio streams cannot be saved to playlists!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=10)
        
        track = player.current
        track_hash = getattr(track, "track_id", None) or track.info.get("track")
        
        if not track_hash:
            embed = discord.Embed(description=f"{Emojis.error} Failed to extract the track details. Please try again.", color=discord.Color.red())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)
            
        if not re.match(r"^[a-zA-Z0-9 ]+$", playlist_name):
            embed = discord.Embed(description=f"{Emojis.warning} Playlist names can only contain letters, numbers, and normal spaces!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)

        raw_input_name = playlist_name.strip()
        normalized_input = raw_input_name.replace(" ", "").lower()
        
        user_playlists = await self.db.get_all_user_playlists(ctx.author.id)
        existing_names = [p[0] for p in user_playlists]
        
        for existing_name in existing_names:
            escaped_existing = re.escape(existing_name.replace(" ", "").lower())
            if re.match(f"^{escaped_existing}$", normalized_input):
                if existing_name.lower() != raw_input_name.lower():
                    embed = discord.Embed(description=f"{Emojis.warning} You already have a playlist named `{existing_name}`! Please use the exact casing to add to it.", color=discord.Color.yellow())
                    return await ctx.reply(embed=embed, ephemeral=True, delete_after=10)

        final_playlist_name = raw_input_name.lower()
        
        if final_playlist_name not in [n.lower() for n in existing_names] and len(user_playlists) >= 5:
            embed = discord.Embed(description=f"{Emojis.warning} You have reached your limit of **5** personal playlists! Delete one before creating a new one.", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=10)

        count = await self.db.get_playlist_track_count(ctx.author.id, final_playlist_name)
        if count >= 30:
            embed = discord.Embed(description=f"{Emojis.warning} Playlists are capped at a maximum of **30** tracks!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=10)

        success = await self.db.add_to_playlist(ctx.author.id, final_playlist_name, track_hash, track.title)
        if not success:
            embed = discord.Embed(description=f"{Emojis.warning} **{track.title}** is already inside the playlist `{final_playlist_name}`!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)

        embed = discord.Embed(
            description=f"{Emojis.success} Saved **{track.title}** to your playlist `{final_playlist_name}`!",
            color=discord.Color.green()
        )
        await ctx.reply(embed=embed, ephemeral=True, delete_after=10)

    @myplaylist.command(
        name="load", 
        description="🎶 Load and play all songs from one of your playlists."
    )
    @app_commands.describe(playlist_name="✨ Enter the name of the playlist to load")
    async def load_playlist(self, ctx: commands.Context, playlist_name: str):
        if not ctx.author.voice:
            embed = discord.Embed(description=f"{Emojis.warning} You must be in a voice channel to load a playlist!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)

        if ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            embed = discord.Embed(description=f"╮(￣ω￣;)╭ You need to join {ctx.voice_client.channel.mention} to use the player!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True)

        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            embed = discord.Embed(description=f"{Emojis.error} The music system is currently unavailable.", color=discord.Color.red())
            return await ctx.reply(embed=embed, ephemeral=True)

        await ctx.defer(ephemeral=False)

        playlist_name = playlist_name.lower().strip()
        tracks = await self.db.get_user_playlist(ctx.author.id, playlist_name)
        
        if not tracks:
            embed = discord.Embed(description=f"{Emojis.warning} I couldn't find a playlist named `{playlist_name}`!", color=discord.Color.yellow())
            return await ctx.interaction.followup.send(embed=embed)

        embed_loading = discord.Embed(
            description=f"📂 Fetching `{len(tracks)}` tracks from your playlist `{playlist_name}`...",
            color=discord.Color.blurple()
        )
        
        loading_msg = await ctx.interaction.followup.send(embed=embed_loading)
        try:
            await loading_msg.delete(delay=10)
        except Exception:
            pass

        if not ctx.voice_client:
            player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
            await player.reset_filters(fast_apply=True)
        else:
            player = cast(Player, ctx.voice_client)

        player.controller = ctx.channel
        added_to_queue_count = 0

        for track_hash, track_title in tracks:
            if player.queue.size >= 30:
                embed_cap = discord.Embed(description="⚠️ *The queue hit its 30-track limit. Skipping the remaining songs.*", color=discord.Color.orange())
                await ctx.channel.send(embed=embed_cap, delete_after=10)
                break
                
            valid_track = None
            try:
                valid_track = await player.build_track(track_hash)
            except Exception:
                pass

            if not valid_track or not getattr(music_cog, 'is_valid', lambda t: True)(valid_track):
                if hasattr(music_cog, 'get_or_search_track'):
                    results = await music_cog.get_or_search_track(ctx, player, track_title, "search")
                    if results and not isinstance(results, pomice.Playlist):
                        for t in results:
                            if getattr(music_cog, 'is_valid', lambda x: True)(t):
                                valid_track = t
                                break

            if valid_track:
                valid_track.requester = ctx.author
                
                if player.is_playing:
                    player.queue.put(valid_track)
                    added_to_queue_count += 1
                else:
                    try:
                        await player.channel.edit(status=None)
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass
                    
                    player.loop = False
                    player.loop_queue = False
                    await player.play(valid_track)
                    
                    try:
                        await player.channel.edit(status=f"{Emojis.auro} Auro Music !")
                    except Exception:
                        pass

        if added_to_queue_count > 0:
            desc = f"{Emojis.success} Loaded **{added_to_queue_count}** tracks into the player!"
            if len(player.queue) > added_to_queue_count:
                desc = f"{Emojis.success} Added **{added_to_queue_count}** tracks from `{playlist_name}` to the end of the queue."
                
            embed_done = discord.Embed(description=desc, color=discord.Color.green())
            await ctx.channel.send(embed=embed_done, delete_after=10)

    @myplaylist.command(
        name="view", 
        description="👁️ View all the tracks saved inside one of your playlists."
    )
    @app_commands.describe(playlist_name="✨ Enter the name of the playlist you want to view")
    async def view_playlist(self, ctx: commands.Context, playlist_name: str):
        playlist_name = playlist_name.lower().strip()
        tracks = await self.db.get_user_playlist(ctx.author.id, playlist_name)
        
        if not tracks:
            embed = discord.Embed(description=f"{Emojis.warning} That playlist is either empty or doesn't exist!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=10)

        pagination_view = PlaylistPagination(ctx.author, playlist_name, tracks)
        pagination_view.update_buttons()
        
        if pagination_view.max_pages <= 1:
            pagination_view.clear_items()
            
        msg = await ctx.reply(embed=pagination_view.get_page_embed(), view=pagination_view)
        pagination_view.message = msg

    @myplaylist.command(
        name="list", 
        description="📋 List all your custom playlists and track counts."
    )
    async def list_playlists(self, ctx: commands.Context):
        rows = await self.db.get_all_user_playlists(ctx.author.id)

        if not rows:
            embed = discord.Embed(description=f"{Emojis.warning} You don't have any playlists yet! Create one using `/myplaylist save [name]`.", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=10)

        embed = discord.Embed(
            title=f"📋 Your Playlists ({len(rows)}/5)",
            color=discord.Color.blurple()
        )
        
        description = ""
        for index, row in enumerate(rows, start=1):
            name = row[0]
            try:
                track_count = len(json.loads(row[1]))
            except Exception:
                track_count = 0
            description += f"`{index:02d}.` **{name.title()}** — `{track_count}` track{'s' if track_count != 1 else ''}\n"

        embed.description = description
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed)

    @myplaylist.command(
        name="delete", 
        description="❌ Delete a track or an entire playlist."
    )
    @app_commands.describe(playlist_name="✨ Enter the playlist name", song_num="🔢 Enter the song number to delete (Leave empty to delete the whole playlist)")
    async def delete_playlist(self, ctx: commands.Context, playlist_name: str, song_num: Optional[int] = None):
        playlist_name = playlist_name.lower().strip()
        
        if song_num is None:
            deleted_count = await self.db.delete_entire_playlist(ctx.author.id, playlist_name)
            if deleted_count == 0:
                embed = discord.Embed(description=f"{Emojis.warning} I couldn't find a playlist named `{playlist_name}`!", color=discord.Color.yellow())
                return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)
            
            embed = discord.Embed(
                description=f"{Emojis.success} Deleted the entire playlist `{playlist_name}` and cleared `{deleted_count}` tracks.",
                color=discord.Color.blurple()
            )
            return await ctx.reply(embed=embed)
            
        tracks = await self.db.get_user_playlist(ctx.author.id, playlist_name)
        if not tracks:
            embed = discord.Embed(description=f"{Emojis.warning} That playlist is empty or doesn't exist!", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)
            
        if song_num < 1 or song_num > len(tracks):
            embed = discord.Embed(description=f"{Emojis.warning} Invalid track number! Please pick a number between 1 and {len(tracks)}.", color=discord.Color.yellow())
            return await ctx.reply(embed=embed, ephemeral=True, delete_after=5)
            
        target_hash, target_title = tracks[song_num - 1]
        await self.db.delete_from_playlist(ctx.author.id, playlist_name, target_hash)
        
        embed = discord.Embed(
            description=f"{Emojis.success} Removed **{target_title}** from your playlist `{playlist_name}`.",
            color=discord.Color.blurple()
        )
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomPlaylists(bot))