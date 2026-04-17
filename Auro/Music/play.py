# Auro Music Discord bot
# Licensed under AGPL-3
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

# Constants for filtering junk
MAX_DURATION = 20 * 60 * 1000
MIN_DURATION = 10 * 1000
env_path = Path(".") / ".env"

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
        self.controller = None
        self.loop = False
        self.loop_queue = False

    async def do_next(self):
        if self.is_playing or self.queue.is_empty:
            return

        try:
            track = self.queue.get()
            await self.play(track)
        except Exception:
            pass


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_time(self, ms: int) -> str:
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"

    def is_valid(self, track: pomice.Track) -> bool:

        if track.is_stream:
            return False
        if not (MIN_DURATION <= track.length <= MAX_DURATION):
            return False
        return True


    async def get_or_search_track(self, player: Player, query: str, search_type: str = "query") -> list:
        
        cached = await player.music_storage.get_cached_track(query)
        
        if cached:
            track_hash, _ = cached
            results = await player.build_track(track_hash)
            return [results] if results else []
        
        if search_type == "spotify":
            results = await player.get_tracks(query=f"ytmsearch:{query}")
            if not results:
                results = await player.get_tracks(query=f"scsearch:{query}")
            source = "Spotify"
        elif search_type == "url":
            results = await player.get_tracks(query=query)
            source = "URL"
        else:  
            results = await player.get_tracks(query=f"ytmsearch:{query}")
            if not results:
                results = await player.get_tracks(query=f"scsearch:{query}")
            source = "YouTube"
        
        
        if results:
            track_hash = getattr(results[0], "track_id", None) or results[0].info.get("track")
            await player.music_storage.save_to_storage(query, track_hash, results[0].title, source)
        
        return results

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
        if player.loop:
            cached_hash = await player.music_cache.get_cached_hash(f"loop_{player.guild.id}")
            if cached_hash:
                loop_track = await player.build_track(cached_hash)
                await asyncio.sleep(0.2)
                return await player.play(loop_track)
        elif player.loop_queue:
            await asyncio.sleep(0.5)
            player.queue.put(track)
            await player.do_next()
        else:
            await asyncio.sleep(0.8)
            await player.do_next()

    @commands.hybrid_command(
        name="play",
        aliases=["p"],
        description="🎶 Play a song from YouTube / SoundCloud / Spotify ",
    )
    @commands.guild_only()
    @app_commands.describe(search="Search for a song or paste a link")
    async def play(self, ctx: commands.Context, *, search: str):
        if not ctx.author.voice:
            return await ctx.reply(f"{Emojis.warning} You must be in a VC!")

        await ctx.defer()

        if not ctx.voice_client:
            player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
            await player.add_filter(pomice.Filter(tag="reset"), fast_apply=True)
        else:
            player = cast(Player, ctx.voice_client)

        player.controller = ctx.channel

        search = search.strip()

        if "open.spotify.com" in search:
            request = sp.track(search)
            query = f"{request['name']} {', '.join([a['name'] for a in request['artists']])}"
            results = await self.get_or_search_track(player, query, "spotify")

        elif search.startswith(("http", "www")):
            results = await self.get_or_search_track(player, search, "url")
        else:
            results = await self.get_or_search_track(player, search, "search")

        if isinstance(results, pomice.Playlist):
            added = 0
            for track in results.tracks:
                if not self.is_valid(track):
                    continue
                track.requester = ctx.author
                player.queue.put(track)
                added += 1

            if added == 0:
                return await ctx.send(
                    f"{Emojis.warning} No suitable tracks found (Filtered Live/Documentaries)."
                )

            if not player.is_playing:
                await player.do_next()

            return await ctx.send(
                f"{Emojis.success} Loaded **{added}** tracks from playlist."
            )

        valid_track = None
        for t in results:
            if self.is_valid(t):
                valid_track = t
                break

        if not valid_track:
            return await ctx.send(
                f"{Emojis.warning} That track was filtered (Live/Too long/Too short)."
            )

        valid_track.requester = ctx.author

        if player.is_playing:
            player.queue.put(valid_track)
            await ctx.send(f"{Emojis.success} Added to queue: **{valid_track.title}**")
        else:
            await player.play(valid_track)
            try:

                await player.channel.edit(status=f"{Emojis.auro} Auro Music !")
            except:
                pass
            await ctx.send(f"{Emojis.success} Playing: **{valid_track.title}**")

    @commands.hybrid_command(
        name="skip", description="⏭️ Skips the current song and plays the next one."
    )
    async def skip(self, ctx):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_playing:
            embed = discord.Embed(
                title=f"{Emojis.warning} Nothing Playing", color=discord.Color.yellow()
            ).set_footer(
                text="Auro Engine • Warning", icon_url=self.bot.user.display_avatar.url
            )
            return await ctx.reply(embed=embed, delete_after=10)
        player.loop = False
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
    async def stop(self, ctx):
        if ctx.voice_client:
            player = cast(Player, ctx.voice_client)
            await player.music_cache.set_cached_hash(f"loop_{ctx.guild.id}", "", "")
            
            
            if player.loop:
                await player.music_storage.save_to_storage(
                    f"loop_{ctx.guild.id}", "", "", "Cleared"
                )
            
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
    async def queue(self, ctx):
        player = cast(Player, ctx.voice_client)
        if not player or (player.queue.is_empty and not player.is_playing):
            embed = discord.Embed(
                description=f"{Emojis.warning} Queue is Empty",
                color=discord.Color.yellow,
            )
            return await ctx.reply(embed=embed, delete_after=15)

        embed = discord.Embed(title="🎶 Current Queue", color=discord.Color.blue())
        if player.is_playing:
            embed.description = f"**Now Playing:** {player.current.title}\n\n"

        queue_text = ""
        for i, t in enumerate(list(player.queue)[:10], 1):
            queue_text += f"{i}. {t.title}\n"

        embed.add_field(name="Up Next", value=queue_text or "No songs in queue.")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="loop",description="🔄️ Toggles looping for the current playing song.")
    @commands.guild_only()
    async def loop(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_playing:
            return await ctx.reply(f"{Emojis.warning} Nothing is playing to loop!")

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
                title=current_track.title
            )
            
            status = "Enabled"
            color = discord.Color.blurple()
        else:
            status = "Disabled"
            color = discord.Color.red()

        embed = discord.Embed(
            description=f"**Looping is now {status}** for: **{player.current.title}**",
            color=color
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
                description=f"{Emojis.warning} I'm not connected to a VC.",
                color=discord.Color.yellow(),
            )
            return await ctx.reply(embed=embed, delete_after=5)

        if len(player.queue) < 1:
            embed = discord.Embed(
                description=f"{Emojis.warning} Only one song playing. Use `/loop` why wasiting my Resources `(◞‸◟；)` ",
                color=discord.Color.yellow(),
            )
            return await ctx.reply(embed=embed, delete_after=11)

        player.loop_queue = not player.loop_queue
        status = "Enabled" if player.loop_queue else "Disabled"
        emoji = Emojis.success if player.loop_queue else Emojis.error
        embed = discord.Embed(
            description=f"{emoji} **Queue Looping is now {status}** ",
            color=discord.Color.blurple() if player.loop_queue else discord.Color.red(),
        ).set_footer(
            text="Auro Engine • Queue System", icon_url=self.bot.user.display_avatar.url
        )
        await ctx.reply(embed=embed)



async def setup(bot):
    await bot.add_cog(Music(bot))
