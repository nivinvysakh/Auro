import discord
from discord.ext import commands
from util.emojis import Emojis
class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error,commands.CommandOnCooldown):
            embed = discord.Embed(
                title=f"{Emojis.cooldown}Command on Cooldown",
                description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
                color=discord.Color.orange()
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
        elif isinstance(error,commands.MissingRequiredArgument):
            embed = discord.Embed(
                title=f"{Emojis.error} Missing Argument",
                description=f"Usage: `{ctx.prefix}{ctx.command} {ctx.command.signature}`",
                color=discord.Color.red()
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
        elif isinstance(error,commands.BadArgument):
            embed = discord.Embed(
                title=f"{Emojis.error} Bad Argument",
                description=str(error),
                color=discord.Color.red()
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
        else:
            embed = discord.Embed(
                title=f"{Emojis.error} An Error Occurred",
                description="An unexpected error occurred while processing your command.",
                color=discord.Color.red()
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
            print(f"Error in command '{ctx.command}': {error}")

async def setup(bot:commands.AutoShardedBot):
    await bot.add_cog(ErrorHandler(bot))