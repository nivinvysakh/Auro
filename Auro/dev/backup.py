import discord
from discord.ext import commands
import os
import shutil
from pathlib import Path
from util.emojis import Emojis

DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "databases" / "DB" / "music_storage.db"
TEMP_BACKUP_PATH = Path(__file__).resolve().parent.parent.parent / "databases" / "DB" / "music_storage_backup.db"

class Backup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="backup", aliases=["bk"])
    @commands.is_owner()
    async def backup(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if not DATABASE_PATH.exists():
            return await ctx.author.send(f"{Emojis.error} Target database file not found at path: `{DATABASE_PATH}`", delete_after=10)

        try:
            shutil.copy2(DATABASE_PATH, TEMP_BACKUP_PATH)
            file = discord.File(TEMP_BACKUP_PATH, filename="music_storage.db")
            
            embed = discord.Embed(
                title=f"{Emojis.success} Storage Backup Complete",
                description=(
                    f"📦 **File Captured:** `music_storage.db`\n"
                    f"⚙️ **System Path:** `{DATABASE_PATH}`\n\n"
                    f"*This is the raw database file containing your permanent user playlists and data.*"
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Auro Core• Binary Pipeline")
            
            await ctx.author.send(embed=embed, file=file, delete_after=10)

            if TEMP_BACKUP_PATH.exists():
                os.remove(TEMP_BACKUP_PATH)

        except Exception as e:
            try:
                await ctx.author.send(f"{Emojis.error} Stealth binary backup failed: `{str(e)}`", delete_after=10)
            except Exception:
                pass
            if TEMP_BACKUP_PATH.exists():
                os.remove(TEMP_BACKUP_PATH)

    @commands.command(name="restore", aliases=["rs"])
    @commands.is_owner()
    async def restore(self, ctx: commands.Context, file: discord.Attachment):
        if not file.filename.endswith('.db'):
            try:
                await ctx.message.delete()
            except Exception:
                pass
            return await ctx.author.send(f"{Emojis.error} Restore aborted: Auro only accepts raw binary database files (`.db`)!", delete_after=10)

        try:
            file_data = await file.to_file()
            
            with open(DATABASE_PATH, "wb") as f:
                f.write(file_data.fp.read())
            
            try :
                await ctx.message.delete()
            except Exception :
                pass

            await ctx.author.send(f"{Emojis.success} **Binary Restore Complete:** Persistent `music_storage.db` has been hot-swapped via param stream!", delete_after=10)

        except Exception as e:
            await ctx.author.send(f"{Emojis.error} Critical Failure during binary file hot-swap stream: `{str(e)}`", delete_after=10)
        
    @commands.command(name="clear_dm", aliases=["cdm"])
    @commands.is_owner()
    async def cdm(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        try:
            dm_channel = ctx.author.dm_channel
            if dm_channel is None:
                dm_channel = await ctx.author.create_dm()

            deleted_count = 0
            async for message in dm_channel.history(limit=100):
                if message.author == self.bot.user:
                    try:
                        await message.delete()
                        deleted_count += 1
                    except Exception:
                        pass

            await ctx.author.send(f"{Emojis.success} DM cache cleared! Removed **{deleted_count}** bot messages.", delete_after=5)

        except Exception as e:
            await ctx.author.send(f"{Emojis.error} Failed to purge DM history: `{str(e)}`", delete_after=10)

async def setup(bot: commands.Bot):
    await bot.add_cog(Backup(bot))