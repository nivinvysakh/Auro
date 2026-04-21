import discord
from discord.ext import commands
from util.emojis import Emojis as emojis
from discord import app_commands
from asyncio import sleep


class PurgeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="clearbot", description="🧹 Clean up all bot responses in the channel!"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clearbot(self, ctx: commands.Context):
        await ctx.defer(ephemeral=True)

        history = [
            m async for m in ctx.channel.history(limit=50) if m.author == self.bot.user
        ]

        if not history:

            return await ctx.interaction.edit_original_response(
                content=f"{emojis.error} No bot messages found in the last 50 messages."
            )

        deleted = await ctx.channel.purge(
            limit=50, check=lambda m: m.author == self.bot.user
        )

        embed = discord.Embed(
            title=f"{emojis.success} Deleted {len(deleted)} bot messages!",
            color=emojis.color,
        )

        await ctx.channel.send(embed=embed, delete_after=10)
        await ctx.interaction.edit_original_response(content="✅ Purge Complete!")

    @commands.hybrid_command(
        name="clearmsg", description="🧹 Clean up messages in the channel!"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(amount="✨ Number of messages to delete (1-100)")
    async def clearmsg(self, ctx: commands.Context, amount: int = 50):
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title=f"{emojis.error} Provide a number between 1 and 100.",
                color=emojis.color,
            )
            return await ctx.reply(embed=embed, delete_after=10)

        await ctx.defer(ephemeral=True)

        messages = await ctx.channel.purge(limit=amount)
        await sleep(1)

        embed = discord.Embed(
            title=f"{emojis.success} Successfully deleted {len(messages)} messages!",
            color=emojis.color,
        )

        await ctx.channel.send(embed=embed, delete_after=10)
        await ctx.interaction.edit_original_response(content="✅ Messages Cleared!")


async def setup(bot):
    await bot.add_cog(PurgeBot(bot))
