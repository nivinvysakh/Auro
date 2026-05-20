import discord
from discord.ext import commands
import os
import sqlite3
from pathlib import Path
from util.emojis import Emojis

DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "databases" / "DB" / "music_storage.db"
TEMP_BACKUP_PATH = Path(__file__).resolve().parent.parent.parent / "databases" / "DB" / "music_storage_backup.db"

class Backup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _ensure_dir(self):
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    async def _safe_delete_trigger(self, ctx: commands.Context):
        try:
            if ctx.guild:
                await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="backup", aliases=["bk"])
    @commands.is_owner()
    async def backup(self, ctx: commands.Context):
        await self._safe_delete_trigger(ctx)
        self._ensure_dir()

        if not DATABASE_PATH.exists():
            return await ctx.author.send(f"{Emojis.error} Target database file not found at path: `{DATABASE_PATH}`")

        try:
            src = sqlite3.connect(DATABASE_PATH)
            dst = sqlite3.connect(TEMP_BACKUP_PATH)
            with dst:
                src.backup(dst)
            src.close()
            dst.close()

            file = discord.File(TEMP_BACKUP_PATH, filename="music_storage.db")
            
            embed = discord.Embed(
                title=f"{Emojis.success} Storage Backup Complete",
                description=(
                    f"📦 **File Captured:** `music_storage.db`\n"
                    f"⚙️ **System Path:** `{DATABASE_PATH}`\n\n"
                    f"⚠️ *Keep this file secure. It contains raw binary information of user data structures.*"
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Auro Core • Safe Binary Pipeline")
            
            await ctx.author.send(embed=embed, file=file)

        except Exception as e:
            try:
                await ctx.author.send(f"{Emojis.error} Stealth binary backup failed: `{str(e)}`")
            except Exception:
                pass
        finally:
            if TEMP_BACKUP_PATH.exists():
                os.remove(TEMP_BACKUP_PATH)

    @commands.command(name="restore", aliases=["rs"])
    @commands.is_owner()
    async def restore(self, ctx: commands.Context):
        await self._safe_delete_trigger(ctx)
        self._ensure_dir()

        if not ctx.message.attachments:
            return await ctx.author.send(f"{Emojis.error} Restore aborted: You must upload/attach a `.db` file when calling this command!")

        target_file = ctx.message.attachments[0]
        if not target_file.filename.endswith('.db'):
            return await ctx.author.send(f"{Emojis.error} Restore aborted: Auro only accepts raw binary database files (`.db`)!")

        try:
            binary_data = await target_file.read()
            
            with open(DATABASE_PATH, "wb") as f:
                f.write(binary_data)

            await ctx.author.send(f"{Emojis.success} **Binary Restore Complete:** Persistent `music_storage.db` has been successfully updated!")

        except Exception as e:
            await ctx.author.send(f"{Emojis.error} Critical Failure during binary file hot-swap stream: `{str(e)}`")
        
    @commands.command(name="clear_dm", aliases=["cdm"])
    @commands.is_owner()
    async def cdm(self, ctx: commands.Context):
        await self._safe_delete_trigger(ctx)

        try:
            dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
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
            await ctx.author.send(f"{Emojis.error} Failed to purge DM history: `{str(e)}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(Backup(bot))