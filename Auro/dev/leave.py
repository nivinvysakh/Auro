import discord
from discord.ext import commands

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklist = [1310970988573229139,1492225309897130014]

    @commands.is_owner()
    @commands.command(name="eject", aliases=["leaveguild", "getout"])
    async def eject(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        
        if not guild:
            return await ctx.send(f"❌ I'm not in a server with ID: `{guild_id}`")

        try:
            await guild.leave()
            await ctx.send(f"✅ Successfully left **{guild.name}**.")
            print(f"{self.bot.get_time()} | ADMIN | Manual Ejection: Left {guild.name} ({guild_id})")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to leave: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id in self.blacklist:
            print(f"{self.bot.get_time()} | SECURITY | Ejecting from Blacklisted Guild: {guild.name} ({guild.id})")
            try:
                await guild.leave()
            except Exception as e:
                print(f"Error during auto-eject: {e}")

async def setup(bot):
    await bot.add_cog(Leave(bot))