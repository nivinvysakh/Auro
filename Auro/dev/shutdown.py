import discord
import asyncio
import pomice
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
            description="Auro Bot will be shutting down in 10 Sec",
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
        try :
            node_pools = pomice.NodePool()
            for node in list(node_pools.nodes.values()):
                await node.disconnect()
                print("Pomice Node successfully disconnected.")
        except Exception as e :
            print(f"Failed to Disconnect due to following Error : {e}")
        finally:
            await self.bot.close()
            print("Discord Connnection Closed.")    
async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Shutdown(bot))