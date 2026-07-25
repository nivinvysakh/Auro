import discord
from discord.ext import commands
from discord import app_commands
from util.emojis import Emojis
from databases import SettingsStorage 
class ChannelGroup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.storage = SettingsStorage()

    @commands.hybrid_group(
        name="channel",
        description="🔒 Manage text channel restrictions for Auro commands."
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def channel_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🔒 Auro Channel Configuration",
                description=(
                    "Use the subcommands to restrict or unlock Auro's text command access:\n\n"
                    f"{Emojis.dot} `a!channel set #channel` - Lock bot to a channel\n"
                    f"{Emojis.dot} `a!channel remove` - Allow bot in all channels"
                ),
                color=discord.Color.blurple()
            )
            await ctx.reply(embed=embed)

    @channel_group.command(
        name="set",
        description="🔒 Restrict all music bot commands to a specific text channel."
    )
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(target_channel="✨ The text channel you want to lock Auro commands to")
    async def channel_set(self, ctx: commands.Context, target_channel: discord.TextChannel):
        self.storage.set_allowed_channel(ctx.guild.id, target_channel.id)

        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"Auro will now only respond to music commands inside {target_channel.mention}!",
            color=discord.Color.green()
        )
        embed.set_footer(text="Auro Engine • Permissions Updated")
        await ctx.reply(embed=embed)

    @channel_group.command(
        name="remove",
        description="🔓 Remove the text channel restriction and allow commands everywhere."
    )
    @commands.has_permissions(manage_guild=True)
    async def channel_remove(self, ctx: commands.Context):
        current_restriction = self.storage.get_allowed_channel(ctx.guild.id)

        if current_restriction:
            self.storage.remove_allowed_channel(ctx.guild.id)
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description="Auro commands can now be used in any text channel across the server.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                description=f"{Emojis.warning} There was no channel restriction set for this server in the database.",
                color=discord.Color.red()
            )
            
        embed.set_footer(text="Auro Engine • Permissions Updated")
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} You need the `Manage Server` permission to use these commands.",
                    color=discord.Color.red()
                ),
                delete_after=10
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelGroup(bot))