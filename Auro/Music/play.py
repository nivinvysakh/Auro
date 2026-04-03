import discord
from discord.ext import commands
import pomice
import asyncio
from util.emojis import Emojis
from discord import app_commands
from typing import cast

class Player(pomice.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = pomice.Queue()
        self.controller = None 

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

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: Player, track: pomice.Track):
        if player.controller:
            embed = discord.Embed(
                title=f"{Emojis.musicplaying} **Now Playing:**",
                description=(
                    f"{Emojis.dot} : {track.title}\n"
                    f"{Emojis.dot} : `{track.author}` \n"
                    f"{Emojis.dot} : `{self.format_time(track.length)}` \n"
                    f"{Emojis.dot} : [Click Here]({track.uri})"
                ),
                color=discord.Color.blurple()
            ).set_thumbnail(url=track.thumbnail).set_footer(
                text="Auro", icon_url=self.bot.user.avatar.url
            )
            
            if hasattr(track, 'requester'):
                embed.add_field(name="Requested by", value=track.requester.mention, inline=True)
            
            await player.controller.send(embed=embed)

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track, reason):
        await asyncio.sleep(1.5)
        await player.do_next()

    @commands.Cog.listener()
    async def on_pomice_track_exception(self, player: Player, track, exception):
        if player.controller:
            embed = discord.Embed(
                title=f"{Emojis.warning} **Playback Error!**",
                description=f"An error occurred with `{track.title}`. Skipping...",
                color=discord.Color.red()
            ).set_footer(text="Auro", icon_url=self.bot.user.avatar.url)
            await player.controller.send(embed=embed, delete_after=20)
            await player.do_next()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id != self.bot.user.id:
            return
        player = cast(Player, member.guild.voice_client)
        if not player: return

        if not before.mute and after.mute:
            if player.is_playing:
                await player.set_pause(True)
                if player.controller:
                    await player.controller.send(f"{Emojis.warning} **Bot Muted.** Paused playback.", delete_after=15)
        elif before.mute and not after.mute:
            if player.is_paused:
                await player.set_pause(False)

    @commands.hybrid_command(name="play", aliases=["p"],description="Play a song from YouTube ")
    @commands.guild_only()
    @app_commands.describe(search="The song name, URL, or Playlist link")
    async def play(self, ctx: commands.Context, *, search: str):
        if not ctx.author.voice:
            return await ctx.reply(f"{Emojis.warning} You must be in a VC!", delete_after=10)
        
        await ctx.defer()

        if not ctx.voice_client:
            player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
        else:
            player = cast(Player, ctx.voice_client)

        player.controller = ctx.channel
        
        query = search if search.startswith("https") else f"ytmsearch:{search}"
        results = await player.get_tracks(query=query)

        if not results:
            return await ctx.send(f"{Emojis.warning} No results found.", delete_after=10)

        if isinstance(results, pomice.Playlist):
            for track in results.tracks:
                track.requester = ctx.author
                player.queue.put(track)
            
            if not player.is_playing:
                await player.do_next()

            embed = discord.Embed(
                title=f"{Emojis.music} **Playlist Loaded**",
                description=f"Added **{len(results.tracks)}** tracks from **{results.name}**",
                color=discord.Color.green()
            ).set_thumbnail(url=results.thumbnail).set_footer(text="Auro", icon_url=self.bot.user.avatar.url)
            return await ctx.send(embed=embed, delete_after=15)

        track = results[0]
        track.requester = ctx.author 

        if player.is_playing:
            player.queue.put(track)
            display_title = track.title if len(track.title) <= 50 else track.title[:47] + "..."
            embed = discord.Embed(
                title=f"{Emojis.music} **Added to Queue**",
                description=f"{Emojis.dot} : {display_title.lower()}\n{Emojis.dot} : `{track.author}`",
                color=discord.Color.green()
            ).set_thumbnail(url=track.thumbnail).set_footer(text="Auro", icon_url=self.bot.user.avatar.url)
            embed.add_field(name="Queue Position", value=f"#{player.queue.count}")
            await ctx.send(embed=embed, delete_after=15)
        else:
            await player.play(track)
            await ctx.send(f"{Emojis.success} **Starting track...**", delete_after=5)

    @commands.hybrid_command(name="skip", aliases=["s"],description="Skip the currently playing song")
    @commands.guild_only()
    async def skip(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_playing:
            return await ctx.reply("⚠️ Nothing playing.")
        await player.stop()
        await ctx.reply(f"{Emojis.success} Skipped!", delete_after=5)

    @commands.hybrid_command(name="stop", aliases=["dc"],description="Stop the music and disconnect from the voice channel")
    async def stop(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.destroy()
            await ctx.reply("👋 Disconnected.", delete_after=5)

    @commands.hybrid_command(name="queue", aliases=["q"],description="View the current music queue")
    @commands.guild_only()
    async def queue(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or (player.queue.is_empty and not player.is_playing):
            return await ctx.reply("⚠️ Queue is empty.")

        embed = discord.Embed(title="🎶 Current Queue", color=discord.Color.blurple())
        if player.is_playing:
            embed.add_field(name="Now Playing", value=f"**{player.current.title}**", inline=False)

        queue_list = list(player.queue)[:5]
        for i, track in enumerate(queue_list, 1):
            embed.add_field(name=f"{i}. {track.title[:40]}", value=f"By `{track.author}`", inline=False)
        
        if player.queue.count > 5:
            embed.set_footer(text=f"And {player.queue.count - 5} more tracks...")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="shufflequeue", aliases=["shuffle"],description="Shuffle the current music queue")
    @commands.guild_only()
    @commands.cooldown(1, 35, commands.BucketType.guild)
    async def shufflequeue(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or player.queue.count < 2:
            return await ctx.reply("⚠️ Not enough tracks to shuffle.")

        embed = discord.Embed(title="🎲 Vote to Shuffle", description=f"React with {Emojis.success} (4 votes needed)")
        embed.add_field(name=f"{Emojis.dot} This command can only be used once every 35 seconds.", value="Only users in the same VC can vote.")
        embed.set_footer(text="Auro", icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.avatar.url)
        message = await ctx.reply(embed=embed)
        await message.add_reaction(Emojis.success)
        await message.add_reaction(Emojis.error)
        

        def check(r, u):
            return (
                r.message.id == message.id and 
                not u.bot and str(r.emoji) in [str(Emojis.success), str(Emojis.error)] 
            )


        try:
            while True:
                res, user = await ctx.bot.wait_for("reaction_add", timeout=30.0, check=check)
                
            
                if  str(res.emoji) == str(Emojis.success):
                    if res.count >= 2:
                        player.queue.shuffle()
                        embed = discord.Embed(
                        title=f"{Emojis.music} **Queue Shuffled!**",
                        description=f"The queue has been shuffled by {user.mention}",
                        ).set_footer(text="Auro", icon_url=self.bot.user.avatar.url)
                        await message.edit(embed=embed)
                        await asyncio.sleep(1.5)
                        await message.delete()
                        return
                elif str(res.emoji) == str(Emojis.error):
                    if res.count >=2:
                        embed = discord.Embed(
                            title=f"{Emojis.error} **Shuffle Cancelled!**",
                            description=f"The shuffle vote has been cancelled.",
                        )
                        await message.edit(embed=embed)
                        await asyncio.sleep(1.5)
                        await message.delete()
                        return

        except asyncio.TimeoutError:
            await message.delete()
    @commands.hybrid_command(name="pause",description="Pause the currently playing song")
    @commands.guild_only()
    async def pause(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_playing:
            return await ctx.reply("⚠️ Nothing playing.")
        await player.set_pause(True)
        await ctx.reply(f"{Emojis.success} Paused!", delete_after=5)
    
    @commands.hybrid_command(name="resume",description="Resume the currently paused song")
    @commands.guild_only()
    async def resume(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_paused:
            return await ctx.reply("⚠️ Nothing paused.")
        await player.set_pause(False)
        await ctx.reply(f"{Emojis.success} Resumed!", delete_after=5)

    @commands.hybrid_command(name="clrqueue", aliases=["clear"],description="Clear the current music queue")
    @commands.guild_only()
    async def clrqueue(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player or not player.is_connected:
            return await ctx.reply("❌ I'm not connected to a voice channel.", ephemeral=True)

        player.queue.clear()
        await ctx.reply(f"{Emojis.success} Queue cleared!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Music(bot))