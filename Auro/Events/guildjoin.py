import discord
from discord.ext import commands
from util.emojis import Emojis
from logs.guild_send import push_webhook
class Guild(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if push_webhook:
            await push_webhook(guild.id, guild.name)
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.view_channel and perms.send_messages:
                embed = discord.Embed(
                    title=f"{Emojis.wave} **Hola** i am Auro.",
                    description=(
                        f"{Emojis.dot} i am just a simple music bot for your server."
                    ),
                    color=discord.Color.blurple()
                )
                embed.add_field(name=f"{Emojis.dot} Commands", value="Use `/help` or `a!help` to see all commands.", inline=False)
                embed.add_field(name=f"{Emojis.dot} Eq_Guide" ,value="Run `/eq_help` to see more info how to setup your own eq.",inline=False)
                embed.add_field(name=f"{Emojis.dot} Setup", value="Make sure you're in a Voice Channel to start playing music.", inline=False)
                embed.add_field(name=f"{Emojis.dot} I want to see your code. ", value="I am build for open source you can checkout the code [repo](https://github.com/ilynivin/Auro)",inline=False)
                embed.set_footer(text="Auro || (*^▽^*)").set_thumbnail(url=self.bot.user.avatar.url).set_image(url="https://giffiles.alphacoders.com/787/78740.gif")
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    continue
                except Exception :
                    pass
                break

async def setup(bot):
    await bot.add_cog(Guild(bot))