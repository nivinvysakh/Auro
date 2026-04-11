import discord
from discord.ext import commands
import time
import psutil
import platform
import pomice
from util.emojis import Emojis as emojis


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.hybrid_command(
        name="stats", description="📊 System and Lavalink Dashboard"
    )
    async def stats(self, ctx: commands.Context):
        await ctx.defer()

        uptime = str(
            time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - self.start_time))
        )
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024

        bot_embed = discord.Embed(
            title="🤖 Auro Bot Core",
            description=f"**Status:** `Online` {emojis.success}",
            color=emojis.color,
        )
        bot_embed.add_field(
            name="🛰️ Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True
        )
        bot_embed.add_field(name="⏳ Uptime", value=f"`{uptime}`", inline=True)
        bot_embed.add_field(
            name="🧠 Memory", value=f"`{memory_usage:.2f} MB`", inline=True
        )
        bot_embed.add_field(
            name="⚙️ Environment",
            value=f"`{platform.system()}` | `Py {platform.python_version()}`",
            inline=False,
        )
        bot_embed.set_footer(text="Auro System Layer")
        bot_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        lava_embed = discord.Embed(title="🎵 Lavalink Media Engine", color=0x5865F2)

        try:
            node = pomice.NodePool.get_node()
            if node and node.is_connected:
                stats = node.stats
                cpu = stats.cpu_process_load * 100
                lava_embed.description = f"**Node:** `Auro` {emojis.success}"
                lava_embed.add_field(
                    name="🎸 Players",
                    value=f"`{stats.players_active}` Playing\n`{stats.players_total}` Total",
                    inline=True,
                )
                lava_embed.add_field(
                    name="⚡ Load",
                    value=f"**Node:** `{cpu:.2f}%` \n**System:** `{stats.cpu_cores}%`",
                    inline=True,
                )
                lava_embed.add_field(
                    name="📦 Version",
                    value=f"`Pomice {pomice.__version__}`",
                    inline=True,
                )
                lava_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            else:
                lava_embed.description = "❌ **Node Offline**"
                lava_embed.color = discord.Color.red()
        except Exception as e:
            print(f"Error occurred while fetching Lavalink stats: {e}")
            lava_embed.description = "⚠️ **Connection Error**"
            lava_embed.color = discord.Color.red()

        lava_embed.set_footer(text="Auro Audio Layer")

        await ctx.send(embeds=[bot_embed, lava_embed])


async def setup(bot):
    await bot.add_cog(Stats(bot))
