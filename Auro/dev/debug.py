import discord
from discord.ext import commands
import platform
import time
import datetime
from typing import cast
from util.emojis import Emojis
from Auro.Music.play import Player

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(
            name="debug"
    )
    @commands.is_owner()
    async def debug(self, ctx: commands.Context):
        total_players = len(self.bot.voice_clients)
        active_players = 0
        total_queued_songs = 0
        
        for vc in self.bot.voice_clients:
            if isinstance(vc, Player):
                if vc.is_playing:
                    active_players += 1
                total_queued_songs += len(vc.queue)

        
        player = cast(Player, ctx.voice_client)
        uptime = str(datetime.timedelta(seconds=int(time.time() - self.start_time)))
        
        embed = discord.Embed(
            title="🛰️ Auro Engine: Universal Diagnostic Report",
            color=discord.Color.dark_grey(),
            timestamp=datetime.datetime.utcnow()
        )

        
        embed.add_field(
            name="🌍 Global Analytics (All Servers)",
            value=(
                f"**Total Players:** `{total_players}`\n"
                f"**Active Streams:** `{active_players}`\n"
                f"**Global Queue:** `{total_queued_songs} tracks`"
            ),
            inline=False
        )

        
        embed.add_field(
            name="💻 Host System",
            value=(
                f"**OS:** `{platform.system()}` | **Uptime:** `{uptime}`\n"
                f"**Guilds:** `{len(self.bot.guilds)}` | **Users:** `{len(self.bot.users)}`"
            ),
            inline=False
        )

        
        if player:
            node = player.node
            
            embed.add_field(
                name=f"🎵 Current Server State ({ctx.guild.name})",
                value=(
                    f"**Node_Status:** {Emojis.success if node.is_connected else Emojis.error}\n"
                    f"**Track:** `{player.current.title if player.current else 'None'}`\n"
                    f"**Volume:** `{player.volume}%` | **Paused:** `{player.is_paused}`\n"
                    f"**Loops:** `S: {player.loop}` | `Q: {player.loop_queue}`\n"
                    f"**Queue:** `{len(player.queue)} songs`"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="🎵 Current Server State",
                value=f"{Emojis.error} `No active player in this guild.`",
                inline=False
            )

        embed.set_footer(text=f"Auro Debug", icon_url=self.bot.user.display_avatar.url)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Debug(bot))