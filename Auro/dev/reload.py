import discord
from discord.ext import commands
from util.emojis import Emojis

class ReloadCog(commands.Cog):
    def __init__(self,bot : commands.Bot):
        self.bot = bot

    @commands.command(
        name="reload",
        aliases=["rl"]
    )
    @commands.is_owner()
    async def reload_cog(self,ctx: commands.Context, module_name : str):
        feature_folders = [
            "Auro/Gen", "Auro/Music", "Auro/dev", "Auro/Errors",
            "Auro/Server", "Auro/Events", "Auro/Website", "Auro/status"
        ]
        found = False
        target_path = None

        for folder in feature_folders:
            folder_clean = folder.split("/")[-1]
            possible_path = f"Auro.{folder_clean}.{module_name}"
            
            if possible_path in self.bot.extensions:
                target_path = possible_path
                found = True
                break
        if not found:
            embed = discord.Embed(
                description=f"{Emojis.error} Module `{module_name}` is not loaded or doesn't exist.",
                color= discord.Color.yellow()
            )
            return await ctx.reply(embed=embed)
        
        try :
            await self.bot.reload_extension(target_path)
            embed = discord.Embed(
                title="⚡ Module Hot-Swapped",
                color= discord.Color.green()
            )
            embed.description = (
                f"{Emojis.dot}  **Extension :** `{target_path}`\n"
                f"{Emojis.dot}  **Status :** `Successfully Reloaded`\n\n"
                f"*Changes deployed instantly without disrupting live shard sessions.*"
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text="Auro Core Infrastructure", icon_url=self.bot.user.avatar.url)
            await ctx.reply(embed=embed,delete_after=10)
        except Exception as e:
            embed = discord.Embed(
                title=f"{Emojis.error} Hot-Swap Failed",
                description=f"```py\n{e}\n```",
                color= discord.Color.red()
            )
            await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReloadCog(bot))