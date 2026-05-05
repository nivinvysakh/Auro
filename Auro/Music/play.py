"""
                                                    Auro Music Player Module
                                                    *-----------------------*

 Licensed under the AGPL-3.0 License (the "License"); you may not use this file except in compliance with the License.
This file has Cog Listerners for handling music playback events, including track start, end, exceptions, and user voice state changes. It also includes commands for playing, skipping, stopping, and managing the music queue etc .
Developed by : ilynivin 💝

"""

import discord
from discord.ext import commands
import pomice
import asyncio
import spotipy
from util.emojis import Emojis
from discord import app_commands
from typing import cast
from spotipy import SpotifyClientCredentials
from databases import MusicCache
from databases import MusicStorage
import os
from pathlib import Path
from Auro.Errors.db_bash import TrackHealer
from ui.selections import TrackSelectionView

# Constants for filtering junk
MAX_DURATION = 20 * 60 * 1000
MIN_DURATION = 10 * 1000
env_path = Path(".") / ".env"
track_healer = TrackHealer()

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=os.getenv("client_id"), client_secret=os.getenv("client_secret")
    )
)


class Player(pomice.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = pomice.Queue()
        self.music_cache = MusicCache()
        self.music_storage = MusicStorage()
        self.manual_pause = False
        self.controller = None
        self.loop = False
        self.loop_queue = False

    async def do_next(self):
        if self.queue.is_empty:
            return

        try:
            track = self.queue.get()
            await self.play(track)
        except Exception as e:
            print(f"Error in do_next: {e}")


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -- Utility Method for Formatting Time ---
    def format_time(self, ms: int) -> str:
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"

    # -- Validation Method to Filter Out Streams and Unreasonably Long/Short Tracks ---
    def is_valid(self, track: pomice.Track) -> bool:

        if track.is_stream:
            return False
        if not (MIN_DURATION <= track.length <= MAX_DURATION):
            return False
        return True

    # --- Helper Method for Track Retrieval and Caching ---
    async def get_or_search_track(
        self, ctx: commands.Context, player: Player, query: str, search_type: str = "query" 
    ) -> list:
        use_loop_cache = player.loop or player.loop_queue
        cached = await player.music_storage.get_cached_track(query)
        if cached:
            track_hash, title = cached
            results = await player.build_track(track_hash)
            return [results] if results else []
        if search_type == "spotify":
            results = await player.get_tracks(query=f"spsearch:{query}")
            if not results:
                results = await player.get_tracks(query=f"ytmsearch:{query}")
            source = "Spotify"
        elif search_type == "url":
            results = await player.get_tracks(query=query)
            source = "URL"
        else:
            results = await player.get_tracks(query=f"ytmsearch:{query}")
            if not results:
                results = await player.get_tracks(query=f"scsearch:{query}")
            source = "YouTube"
        if isinstance(results, pomice.Playlist):
            return results
        if not results:
            return []
        if len(results) > 1 :
            view = TrackSelectionView(results[:5])
            msg = await ctx.send(content=f"🔎 {ctx.author.mention}, multiple results found. Select the correct version:", view=view )
            await view.wait()
            await msg.delete()
            if view.selected_track:
                track_hash = getattr(view.selected_track, "track_id", None) or view.selected_track.info.get("track")
                await player.music_storage.save_to_storage(
                    query=query, 
                    track_hash=track_hash, 
                    title=view.selected_track.title, 
                    source=source
                )
                return [view.selected_track]
            await player.destroy()
            await ctx.reply(f"{ctx.author.mention} No Choice is selected.",delete_after=5)
            return []
        if results:
            track_hash = getattr(results[0], "track_id", None) or results[0].info.get(
                "track"
            )
            title = results[0].title

            existing = await player.music_storage.get_by_track_hash(track_hash)
            if not existing:

                await player.music_storage.save_to_storage(
                    query, track_hash, title, source
                )
            else:

                cached_results = await player.build_track(track_hash)
                if cached_results:
                    results = [cached_results]

            if use_loop_cache:
                await player.music_cache.set_cached_hash(query, track_hash, title)

        return results

    # --- Event Listeners ---

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: Player, track: pomice.Track):

        if isinstance(player.channel, discord.StageChannel):
            try:
                await asyncio.sleep(1)
                await player.guild.me.edit(suppress=False)
            except discord.Forbidden:
                if player.controller:
                    await player.controller.send(
                        f"{Emojis.warning} I need speaker permissions!"
                    )
        if player.loop:
            return

        thumbnail = (
            getattr(track, "thumbnail", None)
            or track.info.get("thumbnail")
            or track.info.get("artworkUrl")
        )
        source = track.info.get("sourceName", "Unknown").capitalize()
        if player.controller:
            embed = (
                discord.Embed(
                    title=f"{Emojis.musicplaying} **Now Playing:**",
                    description=(
                        f"{Emojis.dot} : **{track.title}**\n"
                        f"{Emojis.dot} : `{track.author}` \n"
                        f"{Emojis.dot} : `{self.format_time(track.length)}` \n"
                        f"{Emojis.dot} :  [Click Here]({track.uri})\n"
                    ),
                    color=discord.Color.blurple(),
                )
                .set_thumbnail(url=thumbnail)
                .set_footer(
                    text=f"Auro Engine  |  {source}", icon_url=self.bot.user.avatar.url
                )
            )

            if hasattr(track, "requester"):
                embed.add_field(
                    name="Requested by", value=track.requester.mention, inline=False
                )

            await player.controller.send(embed=embed)

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track, reason):
        if str(reason).upper() == "REPLACED":
            return
        if str(reason).upper() == "load_failed":
            return
        if player.loop:
            cached_hash = await player.music_cache.get_cached_hash(
                f"loop_{player.guild.id}"
            )
            if cached_hash:
                loop_track = await player.build_track(cached_hash)
                await asyncio.sleep(0.2)
                return await player.play(loop_track)
        elif player.loop_queue:
            await asyncio.sleep(0.5)
            player.queue.put(track)
        else:
            await asyncio.sleep(0.8)

        await player.do_next()

    @commands.Cog.listener()
    async def on_pomice_track_exception(
        self, player: Player, track: pomice.Track, exception
    ):
        print(f"⚠️ Track Exception: {track.title}. Initializing Healer...")

        track_healer = TrackHealer()
        new_hash = await track_healer.repair(track.title)

        if new_hash:
            healed_track = await player.build_track(new_hash)
            if healed_track:
                healed_track.requester = getattr(track, "requester", None)

                if not player.is_playing:
                    await player.play(healed_track)
                else:

                    player.queue.put_at_front(healed_track)
                    await player.stop()

                if player.controller:
                    await player.controller.send(
                        embed=discord.Embed(
                            title=f"{Emojis.success} Track Healed",
                            description=f"Successfully healed **{track.title}**. Resuming playback.",
                            color=discord.Color.green(),
                        )
                    )
                return

        if player.controller:
            embed = discord.Embed(
                title=f"{Emojis.warning} Playback Error",
                description=f"Auro failed to heal **{track.title}**.\nSkipping...",
                color=discord.Color.red(),
            ).set_footer(
                text="Auro Engine • AutoHeal",
                icon_url=self.bot.user.display_avatar.url,
            )

            await player.controller.send(embed=embed, delete_after=15)

        await player.stop()

    @commands.Cog.listener()
    async def on_pomice_track_stuck(
        self, player: Player, track: pomice.Track, threshold_ms: int
    ):
        if player.controller:
            embed = discord.Embed(
                title=f"{Emojis.warning} Playback Stuck",
                description=f"Auro detected that **{track.title}** is stuck for over {threshold_ms}ms.\nSkipping to the next track.",
                color=discord.Color.red(),
            )
            await player.controller.send(embed=embed)
            await asyncio.sleep(1)
            await player.stop()

    #  --- Music Playback Commands ---

    @commands.hybrid_command(
        name="play",
        aliases=["p"],
        description="🎶 Play a song from YouTube / SoundCloud / Spotify ",
    )
    @commands.guild_only()
    @app_commands.describe(search="🌛 Search for a song or paste a link")
    async def play(self, ctx: commands.Context, *, search: str):
        lock = self.bot.get_cog("Stopvc")
        if lock and lock.maintenance_lock:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} **Auro Maintenance:** New sessions are currently locked by the developer. [dev]",
                    color= discord.Color.red()
                )
            )
        if not ctx.author.voice:
            return await ctx.reply(f"{Emojis.warning} You must be in a VC!")
        if ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        
        await ctx.defer()

        if not ctx.voice_client:
            player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
            await player.reset_filters(fast_apply=True)
        else:
            player = cast(Player, ctx.voice_client)
        if player.current and player.current.is_stream:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.warning} `play` is not available for Radio",
                    description="Stop the Radio by `a!stop` or `a!skip`",
                    color= discord.Colour.yellow()
                )
            )
        await player.music_cache.clear_guild_cache(ctx.guild.id)
        await player.music_cache.clear_loop_queue(ctx.guild.id)
        player.controller = ctx.channel
        search = search.strip()

        if "open.spotify.com" in search:
            try:
                request = sp.track(search)
            except spotipy.exceptions.SpotifyException:
                await ctx.reply(
                    embed=discord.Embed(
                        description=f"{Emojis.warning} Invalid Spotify track URL. Make sure it's a Track link, not a playlist or album.",
                        color=discord.Color.yellow()
                    )
                )
                return
            query = f"{request['name']} {', '.join([a['name'] for a in request['artists']])}"
            results = await self.get_or_search_track(ctx,player, query, "spotify")

        elif search.startswith(("http", "www")):
            results = await self.get_or_search_track(ctx,player, search, "url")
        else:
            results = await self.get_or_search_track(ctx,player, search, "search")
        if isinstance(results, pomice.Playlist):
            await player.destroy()
            not_supported = discord.Embed(
                title=f"{Emojis.warning} Playlist Not Supported",
                color=discord.Color.orange()
            )
            not_supported.add_field(
                name="What happened?",
                value="Auro doesn't support playlists yet.",
                inline= False
            )
            not_supported.add_field(
                name="What you can do",
                value=(
                    f"{Emojis.dot} Use a **single track link**\n"
                    f"{Emojis.dot} Or search for a song name"
                )
            )
            not_supported.add_field(
                name="Examples",
                value=(
                    "`a!play blinding lights`\n"
                    "`a!play https://youtu.be/...`"
                ),
                inline=False
            )
            not_supported.set_footer(
                    text="Auro Music • Single tracks only",
                    icon_url=self.bot.user.display_avatar.url)
            return await ctx.reply(
                embed=not_supported,
                delete_after=20
            )

        valid_track = None
        for t in results:
            if self.is_valid(t):
                valid_track = t
                break

        if not valid_track:
            return

        valid_track.requester = ctx.author
        if player.is_playing:
            player.queue.put(valid_track)
            await ctx.send(f"{Emojis.success} Added to queue: **{valid_track.title}**")
        else:
            try:
                await player.play(valid_track)
            except Exception as e:
                self.bot.dispatch("pomice_track_exception", player, valid_track, e)
            try:

                await player.channel.edit(status=f"{Emojis.auro} Auro Music !")
            except:
                pass
            await ctx.send(f"{Emojis.success} Playing: **{valid_track.title}**")

    @commands.hybrid_command(
        name="skip", description="⏭️ Skips the current song and plays the next one."
    )
    async def skip(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_playing:
            embed = discord.Embed(
                title=f"{Emojis.warning} Nothing Playing", color=discord.Color.yellow()
            ).set_footer(
                text="Auro Engine • Warning", icon_url=self.bot.user.display_avatar.url
            )
            return await ctx.reply(embed=embed, delete_after=10)
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        if player.current.is_stream:
            await player.stop()
            await player.channel.edit(status=None)
            return await ctx.reply(
                embed= discord.Embed(
                    description=f"{Emojis.success} `Radio` mode switched to `Player` mode",
                    color=discord.Color.blurple()
                )
            )
        player.loop = False
        await player.music_cache.clear_guild_cache(ctx.guild.id)
        current_title = player.current.title
        await player.stop()
        embed = discord.Embed(
            description=f"{Emojis.success} Skipped **{current_title}**",
            color=discord.Color.blurple(),
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="stop", description=" ❌ Stops the music, clears the queue, and leaves."
    )
    async def stop(self, ctx:commands.Context):
        if not ctx.voice_client:
            return await ctx.reply(
                embed= discord.Embed(
                    title=f"{Emojis.warning} I am not connected to a voice channel. ",
                    color= discord.Color.yellow()
                ),
                delete_after=15
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        
        player = cast(Player, ctx.voice_client)
        await player.music_cache.clear_guild_cache(ctx.guild.id)
        await player.music_cache.clear_loop_queue(ctx.guild.id)

        try:
            await player.channel.edit(status=None)
        except:
                pass
        await ctx.voice_client.destroy()
        embed = discord.Embed(
                title=f"{Emojis.success} Session Terminated",
                description="The queue has been cleared and the player has disconnected.",
                color=discord.Color.blurple(),
            ).set_footer(
                text="Auro Engine • Offline", icon_url=self.bot.user.display_avatar.url
            )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="queue", description="🎶 Shows the current song and upcoming tracks."
    )
    async def queue(self, ctx:commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color=discord.Color.yellow()
                )
            )
        if player.queue.is_empty and not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.warning} Auro is currently idle.",
                    description="The queue is empty and nothing is playing! `(￣ω￣;)`",
                    color=discord.Color.yellow()
                )
            )
        if player.current.is_stream:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.musicplaying} Now Playing Live Stream",
                    description=f"[{player.current.title} / `{player.current.author}`]",
                    color= discord.Colour.red()
                ).set_thumbnail(url=self.bot.user.avatar.url)
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )

        embed = discord.Embed(title="🎶 Current Queue", color=discord.Color.blue())
        if player.is_playing:
            embed.description = f"**Now Playing:** {player.current.title}\n\n"
            if (player.current.title).startswith("Auro"):
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            else :
                embed.set_thumbnail(url=player.current.thumbnail)

        queue_text = ""
        for i, t in enumerate(list(player.queue)[:10], 1):
            queue_text += f"{i}. {t.title}\n"

        embed.add_field(name="Up Next", value=queue_text or "No songs in queue.")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="loop", description="🔄️ Toggles looping for the current playing song."
    )
    @commands.guild_only()
    async def loop(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color=discord.Color.yellow()
                )
            )
        if not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} There is no song playing to loop! `(￣ω￣;)`",
                    color=discord.Colour.yellow()
                )
            )
        if player.current.is_stream:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} `Loop` is not available for Radio",
                    color= discord.Colour.yellow()
                )
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        player.loop = not player.loop

        if player.loop:
            current_track = player.current
            track_hash = getattr(player.current, "track_id", None)
            if not track_hash:
                track_hash = current_track.info.get("track")
            if not track_hash:
                return
            await player.music_cache.set_cached_hash(
                query=f"loop_{ctx.guild.id}",
                track_hash=track_hash,
                title=current_track.title,
            )

            status = "Enabled"
            color = discord.Color.blurple()
        else:
            await player.music_cache.clear_guild_cache(ctx.guild.id)
            status = "Disabled"
            color = discord.Color.red()

        embed = discord.Embed(
            description=f"**Looping is now {status}** for: **{player.current.title}**",
            color=color,
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="loopqueue",
        aliases=["lq"],
        description="🔁 Toggles looping for the entire queue.",
    )
    @commands.guild_only()
    async def loop_queue(self, ctx: commands.Context):
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
        if player.current.is_stream:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} `Loop_Queue` is not available for Radio",
                    color= discord.Colour.yellow()
                )
            )
        if len(player.queue) < 1:
            embed = discord.Embed(
                description=f"{Emojis.warning} Only one song playing. Use `/loop` why wasting my Resources `(◞‸◟；)` ",
                color=discord.Color.yellow(),
            )
            return await ctx.reply(embed=embed, delete_after=11)

        player.loop_queue = not player.loop_queue

        if player.loop_queue:

            if player.is_playing:
                current_track = player.current
                track_hash = getattr(
                    current_track, "track_id", None
                ) or current_track.info.get("track")
                await player.music_cache.set_cached_hash(
                    query=f"loop_queue_{ctx.guild.id}_0",
                    track_hash=track_hash,
                    title=current_track.title,
                )

            queue_list = list(player.queue)
            for index, track in enumerate(queue_list, start=1):
                track_hash = getattr(track, "track_id", None) or track.info.get("track")
                await player.music_cache.set_cached_hash(
                    query=f"loop_queue_{ctx.guild.id}_{index}",
                    track_hash=track_hash,
                    title=track.title,
                )
        else:

            await player.music_cache.clear_loop_queue(ctx.guild.id)

        status = "Enabled" if player.loop_queue else "Disabled"
        emoji = Emojis.success if player.loop_queue else Emojis.error
        embed = discord.Embed(
            description=f"{emoji} **Queue Looping is now {status}** ",
            color=discord.Color.blurple() if player.loop_queue else discord.Color.red(),
        ).set_footer(
            text="Auro Engine • Queue System", icon_url=self.bot.user.display_avatar.url
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="pause", description="⏸️ Pauses the current track.")
    @commands.guild_only()
    async def pause(self, ctx:commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
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
                    description=f"{Emojis.warning} There is no song playing to pause! `(￣ω￣;)`",
                    color= discord.Color.yellow()
                )
            )
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {ctx.voice_client.channel.mention if ctx.voice_client else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        await player.set_pause(True)
        player.manual_pause = True
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Paused", color=discord.Color.blurple()
            )
        )

    @commands.hybrid_command(name="resume", description="▶️ Resumes a paused track.")
    @commands.guild_only()
    async def resume(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color=discord.Color.yellow()
                )
            )
        if not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} There is no song playing to resume! `(￣ω￣;)`",
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
        await player.set_pause(False)
        player.manual_pause = False
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Resumed", color=discord.Color.blurple()
            )
        )


async def setup(bot):
    await bot.add_cog(Music(bot))
