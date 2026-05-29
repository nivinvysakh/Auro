import discord
from discord.ext import commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis
from util.track_detail_filter import split_track_title
class Track_details(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def generate_track_embed(self, player: Player, track) -> discord.Embed:
        
        status_flags = []
        if getattr(track, "is_stream", False):
            status_flags.append("🔴 Live")
        if getattr(player, "loop", False) and not getattr(track, "is_stream", False):
            status_flags.append("🔂 Looped")
            
        status_subtitle = " • ".join(status_flags) if status_flags else f"{Emojis.musicplaying} Playback Active"

        
        requester = getattr(track, "requester", "Unknown")
        requester_mention = f"<@{requester}>" if isinstance(requester, int) else str(requester)

        main_title, extra_info = split_track_title(track.title)
        if extra_info:
            formatted_description = f"**[{main_title}]({track.uri})**\n`{extra_info}`\n\n{status_subtitle}\n"
        else :
            formatted_description = f"**[{main_title}]({track.uri})**\n*{status_subtitle}*"
        
        embed = discord.Embed(
            title=f"Track Details {Emojis.music_help}",
            description=formatted_description,
            color=discord.Color.from_rgb(235, 235, 235)
        )

        
        embed.add_field(name="🎙️ Author", value=f"`{track.author}`", inline=True)
        embed.add_field(name="👤 Requested By", value=requester_mention, inline=True)
        embed.add_field(name="🎛️ State", value="`Paused`" if player.is_paused else "`Playing`", inline=True)

        
        if hasattr(track, "title") and track.title.startswith("Auro"):
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        elif getattr(track, "thumbnail", None):
            embed.set_thumbnail(url=track.thumbnail)

        embed.set_footer(text="Auro Engine v1.0.0", icon_url=self.bot.user.display_avatar.url)
        return embed

    @commands.hybrid_command(
        name="track_details",
        description="🪻 Get the details of currently playing song.",
        aliases=["td", "fetchtrack", "details"]
    )
    @commands.guild_only()
    async def details(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        
       
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    title=f"{Emojis.error} No active player found.",
                    description="`＞︿＜`",
                    color=discord.Color.yellow()
                )
            )
        
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in {player.channel.mention if player.channel else 'my channel'}!",
                    color=discord.Color.yellow()
                )
            )
        
        if not player.is_playing or not player.current:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} There is no song playing to fetch details.",
                    color=discord.Color.from_rgb(255, 255, 255)
                )
            )

        
        embed = self.generate_track_embed(player, player.current)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Track_details(bot))