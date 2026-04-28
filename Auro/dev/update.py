import discord
from discord.ext import commands
import subprocess
import os
import platform
from util.emojis import Emojis

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    @commands.is_owner()
    @commands.guild_only()
    async def update(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📡 Auro Engine: Update Sequence",
            description=f"{Emojis.loading} Checking remote repository status...",
            color=discord.Color.blurple()
        )
        msg = await ctx.reply(embed=embed)

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.normpath(os.path.join(current_dir, ".."))
            
            subprocess.run(["git", "fetch"], cwd=project_root, check=True, shell=True)
            
            status = subprocess.check_output(
                ["git", "status", "-uno"], cwd=project_root, shell=True
            ).decode()

            if "Your branch is up to date" in status:
                embed.title = f"{Emojis.warning} System Up to Date"
                embed.description = "The **Main** branch is already up to date with origin."
                embed.color = discord.Color.green()
                return await msg.edit(embed=embed)

            script_path = os.path.normpath(os.path.join(current_dir, "..", "dev", "update.bat"))
            
            if os.path.exists(script_path):
                if platform.system() == "Windows":
                    subprocess.Popen([script_path], shell=True, cwd=project_root)
                
                embed.title = f"{Emojis.success} Update Initialized"
                embed.description = "New commits detected. The update script has been triggered."
                embed.color = discord.Color.gold()
                await msg.edit(embed=embed)
            else:
                embed.title = f"{Emojis.error} Script Missing"
                embed.description = f"Could not locate: `{script_path}`"
                embed.color = discord.Color.red()
                await msg.edit(embed=embed)

        except Exception as e:
            embed.title = f"{Emojis.error} Update Failed"
            embed.description = f"Error: `{str(e)}`"
            embed.color = discord.Color.red()
            await msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Update(bot))