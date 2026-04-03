import discord
from discord.ext import commands
from util.emojis import Emojis
class Contribute(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.hybrid_command(name="contribute",description="Learn how to contribute to Auro")
    async def contribute(self,ctx):
        embed = discord.Embed(title="Contributing to Auro",description="> Thank you for your interest in contributing to Auro! We welcome contributions from the community. Here are some ways you can [contribute:](https://github.com/ilynivin/Auro)",color=discord.Color.blue())
        embed.add_field(name=f"{Emojis.code} Code Contributions",value="If you're a developer, you can contribute by submitting pull requests on our GitHub repository. We appreciate bug fixes, new features, and improvements to existing code.",inline=False)
        embed.add_field(name=f"{Emojis.bug} Bug Reports",value="If you encounter any bugs or issues while using Auro, please report them on our GitHub issue tracker. Providing detailed information about the bug will help us address it more effectively.",inline=False)
        embed.add_field(name=f"✨ Suggestions and Feedback",value="We value your feedback! If you have any suggestions for new features or improvements, please share them with us in the #suggestions channel on our Discord server.",inline=False)
        embed.add_field(name=f"💖 Support and Community Engagement",value="Join our Discord server to engage with the community, ask questions, and offer support to other users. Your participation helps create a welcoming and helpful environment for everyone.",inline=False)
        embed.set_footer(text="Thank you for helping us make Auro better!",icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Contribute(bot))