import discord
from discord.ext import commands
auth_users = [957196694393614367,1464578808202919998]
def is_auth():
    async def predicate(ctx: commands.Context):
        is_owner = await ctx.bot.is_owner(ctx.author)
        return is_owner or ctx.author.id in auth_users
    return commands.check(predicate)
class Rules_send(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
    
    @commands.command(
        name="send_rules"
    )
    @is_auth()
    @commands.cooldown(2,40, commands.BucketType.guild)
    @commands.guild_only()
    async def send_rules(self,ctx:commands.Context):
        embed = discord.Embed(
            title="🌙 Auro Support | Official Server Rules",
            description=(
                "Welcome to the official support home of **Auro**. To ensure a professional "
                "and secure experience for all developers and users, please follow these guidelines.\n\n"
                "**Failure to follow these rules will result in moderation action.**"
            ),
            color=discord.Color.gold()
        )

        
        embed.add_field(
            name="1️⃣ General Conduct",
            value="Be respectful. Harassment, toxicity, or hate speech is strictly prohibited.",
            inline=False
        )
        embed.add_field(
            name="2️⃣ No Spamming",
            value="Avoid excessive pings, emoji spam, or wall-of-text messages.",
            inline=False
        )

        
        embed.add_field(
            name="3️⃣ Cybersecurity & Safety 🔐",
            value=(
                "Strictly no sharing of scam links or malicious payloads. Posting **.exe**, **.zip**, "
                "or **.jpg** files containing hidden malware will result in an immediate ban."
            ),
            inline=False
        )

        
        embed.add_field(
            name="4️⃣ Zero Tolerance Policy 🛑",
            value=(
                "The use of racial slurs (including the N-word), discriminatory language, or "
                "extreme toxicity results in an **immediate and permanent ban**. No appeals."
            ),
            inline=False
        )

        
        embed.add_field(
            name="5️⃣ No NSFW Content",
            value="Auro is a clean environment. No adult imagery, links, or text.",
            inline=False
        )
        embed.add_field(
            name="6️⃣ No Begging",
            value="Do not beg for roles, free premium, or staff attention.",
            inline=False
        )
        
        
        embed.add_field(
            name="7️⃣ No Self-Promotion",
            value="Do not advertise other bots or servers without permission.",
            inline=False
        )
        embed.add_field(
            name="8️⃣ No Ghost Pinging",
            value="Do not ping staff/users and then delete the message.",
            inline=False
        )

        
        embed.add_field(
            name="9️⃣ Support Protocol",
            value="Use the designated forum channels for bug reports. Provide logs/screenshots.",
            inline=False
        )
        embed.add_field(
            name="🔟 English Only",
            value="To allow moderators to help everyone effectively, please use English in public channels.",
            inline=False
        )
        embed.add_field(
            name="⏸️ Neutral Ground 🚫",
            value=(
                "Auro Support is for technical help, music, and coding. Political, "
                "religious, or controversial debates are strictly prohibited to keep "
                "the focus on development."
            ),
            inline=False
        )
        embed.add_field(
            name="🛠️ Efficient Support",
            value=(
                "When asking for help, please provide details. Don't just say 'it's broken.' "
                "Send error logs, describe the issue, and be patient!"
            ),
            inline=False
        )
        embed.add_field(
            name="⚖️ Staff Authority & Appeals",
            value=(
                "Respect the Moderators and Admins; their instructions are final. "
                "However, if you believe a staff decision was incorrect, you may **contact the Server Owner**. "
                "You **must** provide proper evidence (screenshots or screen recordings) for the appeal to be considered."
            ),
            inline=False
        )

        embed.set_footer(text="(●'◡'●)", icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        bot_user = await self.bot.fetch_user(self.bot.user.id)
        embed.set_image(url=bot_user.banner.url)
        await ctx.send(embed=embed)



async def setup(bot: commands.Bot):
    await bot.add_cog(Rules_send(bot))