import discord
from discord.ext import commands
from util.emojis import Emojis

class Avatar(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(
       name="pic",
       description="🖼️ Shows a user's profile picture.",
       aliases=["av", "avatar"] 
    )
    async def pic(self,ctx:commands.Context, member: discord.Member = None):
        target = member or ctx.author
        if target.bot:
            embed= discord.Embed(
                description=f"{Emojis.warning} I can't fetch avatars for other bots! `(￢_￢)`"
            )
            return await ctx.reply(
                embed=embed , ephemeral=True
            )
        embed = discord.Embed(
            title=f"Avatar — {target.name}",
            color= discord.Color.blurple
        )
        embed.set_image(url=target.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(
            embed=embed
        )
    @commands.hybrid_command(
        name="banner",
        description="🚩 Shows a user's profile banner."
    )
    async def banner(self,ctx:commands.Context,member : discord.Member = None):
        target = member or ctx.author
        if target.bot:
            embed= discord.Embed(
                description=f"{Emojis.warning} I can't fetch banners for other bots! `(￢_￢)`"
            )
            return await ctx.reply(
                embed=embed , ephemeral=True
            )
        user = await self.bot.fetch_user(target.id)
        if not user.banner:
            return await ctx.reply(f"{Emojis.warning} **{target.name}** has no banner set!")
        embed = discord.Embed(
            title=f"Banner — {target.name}",
            color=discord.Color.blurple()
        )
        embed.set_image(url=user.banner.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.reply(embed=embed)
async def setup(bot : commands.Bot):
    await bot.add_cog(Avatar(bot))