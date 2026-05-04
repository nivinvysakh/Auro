import discord
from discord.ext import commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class Track_details(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.hybrid_command(
        name="track_details",
        description="🪻 Get the details of currently playing song.",
        aliases=["td","fetchtrack","details"]
    )
    @commands.guild_only()
    async def details(self,ctx:commands.Context):
        player = cast(Player, ctx.voice_client)
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
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
        
        if not player.is_playing:
            return await ctx.reply(
                embed=discord.Embed(
                 description=f"{Emojis.warning} There is no song playing to fetch the details",
                 color= discord.Color.from_rgb(255, 255, 255)
                )
            )
        duration_ms = player.current.length
        position_ms = player.position
        def format_time(ms):
            seconds = int(ms / 1000)
            minutes, seconds = divmod(seconds, 60)
            return f"{minutes:02d}:{seconds:02d}"
        requester = getattr(player.current, "requester", "Unknown")
        if isinstance(requester, int):
            requester = f"<@{requester}>"
        
        result_embed = discord.Embed(
            title=f"{Emojis.musicplaying} Track Analysis",
            color=discord.Color.from_rgb(225,225,225)
        )
        result_embed.add_field(name="🎵 Title", value=f"[{player.current.title}]({player.current.uri})", inline=False)
        result_embed.add_field(name="🎙️ Author", value=f"`{player.current.author}`", inline=False)
        result_embed.add_field(name="👤 Requested By", value=f"`{requester}`", inline=False)
        result_embed.add_field(name="🎛️ Pause Status", value=f"{Emojis.success}" if player.is_paused else f"{Emojis.error}" , inline=False)
        if player.current.is_stream:
            result_embed.add_field(name="⏱️ Progress", value=f"No Progress for live Stream.")
            result_embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        else :
            result_embed.add_field(name="⏱️ Progress", value=f"`{format_time(position_ms)} / {format_time(duration_ms)}`", inline=False)
            result_embed.set_thumbnail(url=player.current.thumbnail)
        result_embed.add_field(name="📡 Live Stream", value=f"{Emojis.success}" if player.current.is_stream else f"{Emojis.error}", inline=False)
        result_embed.add_field(name="⏩ Seekable", value=f"{Emojis.success}" if player.current.is_seekable else f"{Emojis.error}", inline=False)
        if not player.current.is_stream:
            result_embed.add_field(name="🌸 Loop", value=f"{Emojis.success}" if player.loop else f"{Emojis.error}")
        result_embed.set_image(url="https://i.pinimg.com/originals/92/c6/56/92c6565d9a7f1b52361302580bb21e8d.gif")
        result_embed.set_footer(text=f"Auro Engine v1.0.0", icon_url=self.bot.user.display_avatar.url)

        await ctx.reply(embed=result_embed)

async def setup(bot):
    await bot.add_cog(Track_details(bot))