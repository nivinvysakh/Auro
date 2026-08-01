import discord
from discord.ext import commands
from discord.ui import Button , View
from util.emojis import Emojis

class invite(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="invite",
        aliases=["link","add"],
        description="🔗 Get the official invite link"
    )
    async def invite_cmd(self,ctx: commands.Context):
        embed = discord.Embed(
            title=f"{Emojis.auro} Invite Auro to your Server",
            description="Thank you for choosing Auro! Click the button below or the link to add the bot to your server.",
            color= discord.Color.gold()
        )
        embed.add_field(
            name="🔗 Direct Link",
            value="[Click Here to Invite](https://auroweb.netlify.app)",
            inline= False
        )
        avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=avatar_url)
        
        button = Button(
            label="Invite Auro",
            url="https://auroweb.netlify.app",
            emoji= "🔗"
        )
        view = View()
        view.add_item(button)

        await ctx.reply(
            embed=embed , view=view
        )

async def setup(bot : commands.Bot):
    await bot.add_cog(invite(bot))