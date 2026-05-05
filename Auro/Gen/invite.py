import discord
from discord.ext import commands
from util.emojis import Emojis

class invite(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.hybrid_command(
        name="invite",
        aliases=["link","add"],
        description="🔗 Get the official invite link"
    )
    async def invite(self,ctx: commands.Context):
        embed = discord.Embed(
            title=f"{Emojis.auro} Invite Auro to your Server ",
            description=(
                "[Invite Me](https://aurobot.netlify.app/)"
            ),
            color= discord.Color.blurple
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(
            embed=embed
        )

async def setup(bot):
    await bot.add_cog(invite(bot))