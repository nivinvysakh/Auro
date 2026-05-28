import discord
from discord.ext import commands

class Mention(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def mention_help(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
            
        if isinstance(message.channel, discord.DMChannel):
            return
        

        if message.content in [f"<@{self.bot.user.id}>", f"<@!{self.bot.user.id}>"]:

            if not message.author.guild_permissions.manage_guild:
                
                channel_cog = self.bot.get_cog("ChannelGroup")
                if channel_cog:
                    allowed_channel_id = channel_cog.storage.get_allowed_channel(message.guild.id)
                    
                    if allowed_channel_id and message.channel.id != allowed_channel_id:
                        return

            help_command = self.bot.get_command("help")
            if help_command:
                ctx = await self.bot.get_context(message)
                await ctx.invoke(help_command)

async def setup(bot: commands.Bot):
    await bot.add_cog(Mention(bot))