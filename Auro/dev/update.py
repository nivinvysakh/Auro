import discord
from discord.ext import commands
import subprocess
import os
import platform


class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    @commands.is_owner()
    @commands.guild_only()
    async def update(self, ctx: commands.Context):
        await ctx.reply("📡 **Auro Engine:** Locating update script...")

        try:

            current_dir = os.path.dirname(os.path.abspath(__file__))

            script_ext = ".bat"
            script_path = os.path.normpath(
                os.path.join(current_dir, "..", "dev", f"update{script_ext}")
            )

            if not os.path.exists(script_path):
                return await ctx.send(
                    f"❌ **Path Error:** Could not find `{script_path}`"
                )

            if platform.system() == "Windows":
                project_root = os.path.normpath(os.path.join(current_dir, ".."))
                subprocess.Popen([script_path], shell=True, cwd=project_root)

        except Exception as e:
            await ctx.send(f"⚠️ **Update Trigger Failed:** `{e}`")


async def setup(bot):
    await bot.add_cog(Update(bot))
