import discord
from discord.ext import commands
import pomice
import asyncio
from util.emojis import Emojis
from discord import app_commands
import time 
class Player(pomice.Player):
    """Custom Player for Auro's Music Engine."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()
        self.controller = None # The channel to send updates to

    async def do_next(self):
        """Logic to play the next song automatically."""
        if self.is_playing:
            return
        
        try:
           
            track = await self.queue.get()
            await self.play(track)
            if self.controller:
                await self.controller.send(f"🍃 **Now Playing:** `{track.title}`")
        except Exception:
            pass

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def format_time(self,ms):
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track, reason):
        """Triggered automatically when a track finishes."""
        await player.do_next()

    @commands.hybrid_command(name="play", aliases=["p"], description="Play music from YouTube")
    @app_commands.describe(search = "The song name or URL to search and play")
    async def play(self, ctx: commands.Context, *, search: str):
        """Searches and plays a song."""
        if not ctx.author.voice:
            return await ctx.reply("⚠️ You need to be in a voice channel!")

        
        if not ctx.voice_client:
            player = await ctx.author.voice.channel.connect(cls=Player,self_deaf=True)
        else:
            player = ctx.voice_client

        player.controller = ctx.channel

        
        results = await player.get_tracks(query=f"ytmsearch:{search}")
        if not results:
            return await ctx.reply("❌ No results found on YouTube.")

        track = results[0]

        
        if player.is_playing:
            await player.queue.put(track)
            track_added_embed = discord.Embed(
                title=f"{Emojis.music} **Added to Queue**",
                description=f"{Emojis.dot} : {track.title}\n {Emojis.dot}  : `{track.author}` \n {Emojis.dot}  : `{self.format_time(track.length)}` \n {Emojis.dot}  : [Click Here]({track.uri})",
            ).set_thumbnail(url=track.thumbnail).set_footer(text="Auro",icon_url=self.bot.user.avatar.url)
            await ctx.reply(embed=track_added_embed,delete_after=10)
        else:
            play_embed = discord.Embed(
                title=f"{Emojis.musicplaying} *Now Playing*",
                description=f"{Emojis.dot} : {track.title}\n {Emojis.dot}  : `{track.author}` \n {Emojis.dot}  : `{self.format_time(track.length)}` \n {Emojis.dot}  : [Click Here]({track.uri})",
            )
            play_embed.add_field(name="Requested by", value=ctx.author.mention, inline=False)
            play_embed.add_field(name="Total Tracks in Queue", value=str(player.queue.qsize()), inline=False)
            play_embed.set_footer(text="Auro",icon_url=self.bot.user.avatar.url)
            play_embed.set_thumbnail(url=track.thumbnail)
            await player.play(track)
            await time.sleep(0.5)
            await ctx.reply(embed=play_embed)

    @commands.hybrid_command(name="skip", aliases=["s"], description="Skip the current song")
    async def skip(self, ctx: commands.Context):
        """Skips the current track."""
        player = ctx.voice_client
        if not player or not player.is_playing:
            skip_embed = discord.Embed(
                title=f"{Emojis.warning} **Nothing is playing!**",
                description="There is no track to skip.",
            )
            await ctx.reply(embed=skip_embed)
        else :
            skip_embed = discord.Embed(
                title=f"{Emojis.success} **Track Skipped!**",
                description="The current track has been skipped."
            )

            await ctx.reply(embed=skip_embed,delete_after=5)
            
        
        await player.stop()
        

    @commands.hybrid_command(name="stop", aliases=["dc"], description="Stop music and leave")
    async def stop(self, ctx: commands.Context):
        """Destroy the player and leave VC."""
        player = ctx.voice_client
        if player:
            await player.destroy()
            await ctx.reply("🛑 **Stopped. Vibes: Cleared.**")
        else:
            await ctx.reply("I'm not in a voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))