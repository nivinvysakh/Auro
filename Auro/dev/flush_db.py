import discord
from discord.ext import commands
import asyncio
from databases import MusicStorage, MusicCache
from util.emojis import Emojis

class Flush(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.music_db = MusicStorage()
        self.music_cache = MusicCache()

    @commands.command(name="flush")
    @commands.is_owner()
    async def flush(self, ctx: commands.Context, days: int = 30):
        storage = self.music_db

        if not storage:
            embed = discord.Embed(
                title="❌ Error",
                description="Music Storage instance not found on bot.",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="🧹 Database Flush",
            description=f"Clear tracks older than **{days} days**?\n\nType `confirm` to proceed.",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.content.lower() == "confirm"

        try:
            await self.bot.wait_for("message", check=check, timeout=15.0)
            await storage.selective_flush(days)
            embed = discord.Embed(
                title="✅ Success",
                description="Database flushed and optimized.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏱️ Timeout",
                description="Confirmation timed out after 15 seconds.",
                color=discord.Color.orange(),
            )
            await ctx.send(embed=embed)

    @commands.command(name="flushall")
    @commands.is_owner()
    async def flush_all(self, ctx: commands.Context):
        storage = self.music_db

        if not storage:
            embed = discord.Embed(
                title="❌ Error",
                description="Music Storage instance not found on bot.",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="🧹 Full Database Flush",
            description="Clear **ALL** cached tracks permanently?\n\nType `confirm` to proceed.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.content.lower() == "confirm"

        try:
            await self.bot.wait_for("message", check=check, timeout=15.0)
            await storage.flush_all()
            embed = discord.Embed(
                title="✅ Success",
                description="All cached tracks deleted and database optimized.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏱️ Timeout",
                description="Confirmation timed out after 15 seconds.",
                color=discord.Color.orange(),
            )
            await ctx.send(embed=embed)

    @commands.command(name="flushsong")
    @commands.is_owner()
    async def flush_song(self, ctx: commands.Context, *, song_name: str):
        embed = discord.Embed(
            title="🧹 Flush Target Song",
            color=discord.Color.from_rgb(241, 196, 15)
        )
        embed.description = (
            f"{Emojis.dot} **Target Query :** `{song_name}`\n\n"
            f"*This will drop all database rows matching this track text name from storage.*\n"
            f"Please type `confirm` within 15 seconds to proceed."
        )
        embed.set_footer(text="Auro Engine • Cache Manager", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.content.lower() == "confirm" and m.channel == ctx.channel

        try:
            await self.bot.wait_for("message", check=check, timeout=15.0)
            
            storage_removed = await self.music_db.delete_by_title(song_name)

            success_embed = discord.Embed(
                title="⚡ Storage Eviction Complete",
                color=discord.Color.from_rgb(46, 204, 113)
            )
            success_embed.description = (
                f"{Emojis.dot} **Target Track :** `{song_name}`\n"
                f"{Emojis.dot} **Storage Dropped :** `{storage_removed} rows`\n\n"
                f"*The permanent database layer was re-indexed and optimized successfully.*"
            )
            success_embed.set_footer(text="Auro Engine • Cache Manager", icon_url=self.bot.user.avatar.url)
            await ctx.reply(embed=success_embed)

        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏱️ Flush Timeout",
                description=f"{Emojis.warning} Confirmation timed out. Operation canceled safely.",
                color=discord.Color.orange()
            )
            await ctx.reply(timeout_embed)

    @commands.command(name="cachedump")
    @commands.is_owner()
    async def cache_dump(self, ctx: commands.Context):

        await ctx.defer()

        cache_data = await self.music_cache.get_all()
        storage_data = await self.music_db.get_all()

        embeds = []

        cache_embed = discord.Embed(
            title="🗂️ Music Cache Data (Loop) ",
            color=discord.Color.blurple(),
            description=f"Total entries: **{len(cache_data)}**",
        ).set_thumbnail(url=self.bot.user.avatar.url)

        if cache_data:
            for i, (query, track_hash, title) in enumerate(cache_data[:25], 1):

                short_hash = (
                    track_hash[:20] + "..." if len(track_hash) > 20 else track_hash
                )
                cache_embed.add_field(
                    name=f"{i}. {query[:50]}",
                    value=f"**Hash:** `{short_hash}`\n**Title:** {title[:60]}",
                    inline=False,
                )
        else:
            cache_embed.description += "\n\n*No cache entries*"

        cache_embed.set_footer(
            text=f"Showing {min(25, len(cache_data))} of {len(cache_data)} entries",
            icon_url=self.bot.user.avatar.url,
        )
        embeds.append(cache_embed)

        storage_embed = discord.Embed(
            title="💾 Music Storage Data",
            color=discord.Color.green(),
            description=f"Total entries: **{len(storage_data)}**",
        ).set_thumbnail(url=self.bot.user.avatar.url)

        if storage_data:
            for i, (query, track_hash, title, source) in enumerate(
                storage_data[:20], 1
            ):

                short_hash = (
                    track_hash[:20] + "..." if len(track_hash) > 20 else track_hash
                )
                storage_embed.add_field(
                    name=f"{i}. {query[:50]}",
                    value=f"**Hash:** `{short_hash}`\n**Title:** {title[:60]}\n**Source:** {source}",
                    inline=False,
                )
        else:
            storage_embed.description += "\n\n*No storage entries*"

        storage_embed.set_footer(
            text=f"Showing {min(20, len(storage_data))} of {len(storage_data)} entries",
            icon_url=self.bot.user.avatar.url,
        )
        embeds.append(storage_embed)

        summary_embed = discord.Embed(
            title="📈 Cache Summary", color=discord.Color.gold()
        ).set_thumbnail(url=self.bot.user.avatar.url)
        summary_embed.add_field(
            name="🗂️ Cache Entries (Loop)", value=str(len(cache_data)), inline=True
        )
        summary_embed.add_field(
            name="💾 Storage Entries", value=str(len(storage_data)), inline=True
        )
        summary_embed.add_field(
            name="Total Unique Tracks", value=str(len(storage_data)), inline=True
        )
        summary_embed.set_footer(
            text="Auro Engine • Cache Manager", icon_url=self.bot.user.avatar.url
        )
        embeds.append(summary_embed)

        await ctx.reply(embeds=embeds)


async def setup(bot : commands.Bot):
    await bot.add_cog(Flush(bot))
