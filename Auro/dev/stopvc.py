import discord
from discord.ext import commands
from util.emojis import Emojis

class Stopvc(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        self.maintenance_lock = False

    @commands.command(name="forcestop",aliases=["fs","maintenance"])
    @commands.is_owner()
    async def forcestop(self, ctx: commands.Context):
        
        active_clients = list(self.bot.voice_clients)
        total_players = len(active_clients)

        if total_players == 0:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.success} No active sessions found. Safe to update.",
                    color=discord.Color.green()
                )
            )

        for player in active_clients:
            try:
                controller = getattr(player, 'controller', None)
                
                if controller:
                    await controller.send(
                        embed=discord.Embed(
                            title=f"{Emojis.warning} **Auro Maintenance Alert**",
                            description=(
                                "An upcoming update is scheduled. \n"
                                "To prevent ghost sessions, I have stopped playing in this VC."
                            ),
                            color=discord.Color.red()
                        )
                    )
                await player.channel.edit(status=None)
                await player.stop()
                await player.destroy()
                
            except Exception as e:
                print(f"Error ejecting session: {e}")
                continue

        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Force stop complete.",
                description=f"**{total_players}** sessions successfully ejected.",
                color= discord.Color.green()
            )
        )
    @commands.command(
        name="lock",
        aliases=["lvc"]
    )
    @commands.is_owner()
    async def lock(self,ctx: commands.Context):
        self.maintenance_lock = True
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Lock is Active",
                description=f"{Emojis.dot} play command and radio command has been locked",
                color= discord.Colour.red()
            )
        )
    @commands.command(
        name="unlock",
        aliases=["uvc"]
    )
    @commands.is_owner()
    async def unlock(self, ctx: commands.Context):
        self.maintenance_lock = False
        await ctx.reply(
            embed=discord.Embed(
                title=f"{Emojis.success} Play and radio commands are unlocked",
                description="Any one can now start using play or radio command",
                color=discord.Color.green()
            )
        )
        
async def setup(bot : commands.Bot):
    await bot.add_cog(Stopvc(bot))