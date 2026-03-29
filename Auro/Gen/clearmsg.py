import discord
from discord.ext import commands
from util.emojis import Emojis as emojis

class PurgeBot(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot

    @commands.hybrid_command(name="purgebot", description="🧹 Clean up all bot responses in the channel!")
    async def purgebot(self, ctx: commands.Context):
        await ctx.defer()

        def is_bot_message(message):
            return message.author == self.bot.user

        deleted = await ctx.channel.purge(limit=50, check=is_bot_message)

        await ctx.reply(
            embed=discord.Embed(
                title=f"{emojis.success} Successfully deleted {len(deleted)} bot messages!",
                color= emojis.color
            ),
            delete_after=10
        )

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(PurgeBot(bot=bot))