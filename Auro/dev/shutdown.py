import discord
import asyncio
from discord.ext import commands

class Shutdown(commands.Cog):
    def __init__(self, bot : commands.AutoShardedBot):
        self.bot = bot
    
    @commands.command(
        name="shutdown",
        aliases=["cq"]
    )
    @commands.is_owner()
    async def shutdown(self,ctx : commands.Context):
        embed = discord.Embed(
            title="🛑 Shutdown Started.",
            description="eta 10 sec..",
            color= discord.Color.red()
        )
        embed.set_footer(
            text=f" Requested by Developer : {ctx.author.name}",
            icon_url= self.bot.user.avatar.url
        )
        await ctx.send(
            embed=embed
        )
        await asyncio.sleep(10)
        print("Connection Close Request from Discord Msg Trigger.")
        await self.bot.close()
    
async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Shutdown(bot))