import discord
from discord.ext import commands

class Mention(commands.Cog):
    def __init__(self,bot : commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def mention_help(self, message: discord.Message):
        
        if message.author.bot or not message.guild:
            return
        if isinstance(message.channel , discord.DMChannel):
            return
        
        if message.content == f"<@{self.bot.user.id}>" or message.content == f"<@!{self.bot.user.id}>":
            
            help_command = self.bot.get_command("help")
            if help_command:
                ctx = await self.bot.get_context(message)
                await ctx.invoke(help_command)

async def setup(bot : commands.Bot):
    await bot.add_cog(Mention(bot))
