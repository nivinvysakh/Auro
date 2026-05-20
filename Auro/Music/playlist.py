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

    def get_page_embed(self) -> discord.Embed:
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_tracks = self.tracks[start:end]

        embed = discord.Embed(
            title=f"📂 Playlist: {self.playlist_name.title()}",
            color=discord.Color.blurple()
        )
        
        description = ""
        for index, (track_hash, track_title) in enumerate(page_tracks, start=start + 1):
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
                    description=f"{Emojis.warning} This interaction menu isn't for you!",
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
        description="📂 Manage your personal saved Auro playlists."
    )
    @app_commands.describe(
        playlist_name = "✨ The name of the Playlist."
    )
    @commands.guild_only()
    async def myplaylist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Invalid usage! Use `/myplaylist save`, `/myplaylist load`, `/myplaylist view`, or `/myplaylist list`.",
                    color=discord.Color.yellow()
                ), delete_after=5
            )

    @myplaylist.command(
        name="save", 
        description="💾 Save the currently playing song to a custom personal playlist."
    )
    @app_commands.describe(
        playlist_name = "✨ The name of the Playlist."
    )
    async def save_track(self, ctx: commands.Context, playlist_name: str):
        if not ctx.author.voice:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} You must be connected to a voice channel to save tracks!",
                    color=discord.Color.yellow()
                ), delete_after=5
            )
        
        player = cast(Player, ctx.voice_client)
        if not player or not player.current:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Nothing is playing right now to save!",
                    color=discord.Color.yellow()
                ), delete_after=5
            )
        if player.current.is_stream:
            embed = discord.Embed(
                description=f"{Emojis.warning} Radio live streams cannot be saved to personal playlists!",
                color=discord.Color.yellow()
            )
            return await ctx.reply(
                embed=embed, ephemeral=True, delete_after=15
            )
        
        track = player.current
        track_hash = getattr(track, "track_id", None) or track.info.get("track")
        
        if not track_hash:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.error} Failed to extract track data identifier.",
                    color=discord.Color.red()
                ), delete_after=5
            )
        if not re.match(r"^[a-zA-Z0-9 ]+$", playlist_name):
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Playlist names can only contain alphabetic letters and spaces!",
                    color=discord.Color.yellow()
                ), delete_after=5
            )

        raw_input_name = playlist_name.strip()
        normalized_input = raw_input_name.replace(" ", "").lower()
        
        user_playlists = await self.db.get_all_user_playlists(ctx.author.id)
        existing_names = [p[0] for p in user_playlists]
        
        for existing_name in existing_names:
            escaped_existing = re.escape(existing_name.replace(" ", "").lower())
            if re.match(f"^{escaped_existing}$", normalized_input):
                if existing_name.lower() != raw_input_name.lower():
                    return await ctx.reply(
                        embed=discord.Embed(
                            description=f"{Emojis.warning} You already have a playlist named `{existing_name}`! Please use the exact name layout or choose a different one to avoid duplicates.",
                            color=discord.Color.yellow()
                        ), delete_after=10
                    )

        final_playlist_name = raw_input_name.lower()
        
        if final_playlist_name not in [n.lower() for n in existing_names] and len(user_playlists) >= 5:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} You have reached your limit of **5** personal playlists! Delete one before creating a new one.",
                    color=discord.Color.yellow()
                ), delete_after=10
            )

        count = await self.db.get_playlist_track_count(ctx.author.id, final_playlist_name)
        if count >= 30:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Personal custom playlists are capped at 30 tracks max!",
                    color=discord.Color.yellow()
                ), delete_after=10
            )

        success = await self.db.add_to_playlist(ctx.author.id, final_playlist_name, track_hash, track.title)
        
        if not success:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} **{track.title}** is already inside playlist `{final_playlist_name}`!",
                    color=discord.Color.yellow()
                ), delete_after=5
            )

        embed = discord.Embed(
            description=f"{Emojis.success} Saved **{track.title}** into your personal playlist `{final_playlist_name}`!",
            color=discord.Color.green()
        )
        await ctx.reply(embed=embed, delete_after=10)

    @myplaylist.command(
        name="load", 
        description="🎶 Load and play all songs from one of your personal playlists."
    )
    @app_commands.describe(
        playlist_name = "✨ The name of the Playlist."
    )
    async def load_playlist(self, ctx: commands.Context, playlist_name: str):
        if not ctx.author.voice:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} You must be in a VC!",
                    color=discord.Color.yellow()
                ), delete_after=5
            )

        if ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )

        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.error} Music core engine not found.",
                    color=discord.Color.red()
                ), delete_after=5
            )

        playlist_name = playlist_name.lower().strip()
        tracks = await self.db.get_user_playlist(ctx.author.id, playlist_name)
        
        if not tracks:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} No personal playlist found matching the name `{playlist_name}`!",
                    color=discord.Color.yellow()
                ), delete_after=10
            )

        await ctx.reply(
            embed=discord.Embed(
                description=f"📂 Loading `{len(tracks)}` tracks from your personal layout `{playlist_name}`...",
                color=discord.Color.blurple()
            ), delete_after=10
        )

        if not ctx.voice_client:
            player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
            await player.reset_filters(fast_apply=True)
        else:
            player = cast(Player, ctx.voice_client)

        player.controller = ctx.channel
        added_to_queue_count = 0

        for track_hash, track_title in tracks:
            if player.queue.size >= 30:
                await ctx.send(
                    embed=discord.Embed(
                        description="⚠️ *Queue capped out at 30 items. Remaining playlist skipped.*",
                        color=discord.Color.orange()
                    ), delete_after=10
                )
                break
                
            try:
                valid_track = await player.build_track(track_hash)
            except Exception:
                valid_track = None

            if not valid_track or not music_cog.is_valid(valid_track):
                results = await music_cog.get_or_search_track(ctx, player, track_title, "search")
                if results and not isinstance(results, pomice.Playlist):
                    for t in results:
                        if music_cog.is_valid(t):
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
                        await asyncio.sleep(1)
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
            if len(player.queue) > added_to_queue_count :
                embed = discord.Embed(
                    description=f"{Emojis.success} Added **{added_to_queue_count}** tracks from `{playlist_name}` at the end of the queue.",
                    color= discord.Color.green()
                )
                await ctx.send(
                    embed= embed,
                    delete_after=10
                )
            else :
                embed = discord.Embed(
                    description=f"{Emojis.success} Added **{added_to_queue_count}** tracks from `{playlist_name}` into the player queue.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed, delete_after=10)

    @myplaylist.command(
        name="view", 
        description="👁️ View all the tracks saved inside one of your custom playlists."
    )
    @app_commands.describe(
        playlist_name = "✨ The name of the Playlist."
    )
    async def view_playlist(self, ctx: commands.Context, playlist_name: str):
        playlist_name = playlist_name.lower().strip()
        tracks = await self.db.get_user_playlist(ctx.author.id, playlist_name)
        
        if not tracks:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} No personal playlist found matching the name `{playlist_name}`!",
                    color=discord.Color.yellow()
                ), delete_after=10
            )

        pagination_view = PlaylistPagination(ctx.author, playlist_name, tracks)
        pagination_view.update_buttons()
        
        if pagination_view.max_pages <= 1:
            pagination_view.clear_items()
            
        msg = await ctx.reply(embed=pagination_view.get_page_embed(), view=pagination_view)
        pagination_view.message = msg

    @myplaylist.command(
        name="list", 
        description="📋 List all your personal custom playlists and their track counts."
    )
    async def list_playlists(self, ctx: commands.Context):
        rows = await self.db.get_all_user_playlists(ctx.author.id)

        if not rows:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} You haven't created any custom playlists yet! Use `/myplaylist save [name]` to start one.",
                    color=discord.Color.yellow()
                ), delete_after=10
            )

        embed = discord.Embed(
            title=f"📋 Your Saved Playlists ({len(rows)}/5)",
            color=discord.Color.blurple()
        )
        
        description = ""
        for index, row in enumerate(rows, start=1):
            name = row[0]
            track_count = len(json.loads(row[1]))
            description += f"`{index:02d}.` **{name.title()}** Layout — `{track_count}` track{'s' if track_count != 1 else ''}\n"

        embed.description = description
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed)

    @myplaylist.command(
        name="delete", 
        description="❌ Delete a track or an entire personal playlist."
    )
    @app_commands.describe(playlist_name="✨ The name of the Playlist.", song_num="🔢 Number of the song to remove (Leave empty to clear entire playlist).")
    async def delete_playlist(self, ctx: commands.Context, playlist_name: str, song_num: Optional[int] = None):
        playlist_name = playlist_name.lower().strip()
        
        if song_num is None:
            deleted_count = await self.db.delete_entire_playlist(ctx.author.id, playlist_name)
            if deleted_count == 0:
                return await ctx.reply(
                    embed=discord.Embed(
                        description=f"{Emojis.warning} No playlist found matching the name `{playlist_name}`!",
                        color=discord.Color.yellow()
                    ), delete_after=5
                )
            
            embed = discord.Embed(
                description=f"{Emojis.success} Successfully deleted the entire playlist `{playlist_name}` (`{deleted_count}` tracks cleared).",
                color=discord.Color.blurple()
            )
            return await ctx.reply(embed=embed, delete_after=10)
            
        tracks = await self.db.get_user_playlist(ctx.author.id, playlist_name)
        if not tracks:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} No playlist found matching the name `{playlist_name}`!",
                    color=discord.Color.yellow()
                ), delete_after=5
            )
            
        if song_num < 1 or song_num > len(tracks):
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Invalid song number! Choose between 1 and {len(tracks)}.",
                    color=discord.Color.yellow()
                ), delete_after=5
            )
            
        target_hash, target_title = tracks[song_num - 1]
        await self.db.delete_from_playlist(ctx.author.id, playlist_name, target_hash)
        
        embed = discord.Embed(
            description=f"{Emojis.success} Removed **{target_title}** from your playlist `{playlist_name}`.",
            color=discord.Color.blurple()
        )
        await ctx.reply(embed=embed, delete_after=10)

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomPlaylists(bot))