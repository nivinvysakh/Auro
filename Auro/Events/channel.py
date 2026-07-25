import discord
from discord.ext import commands
from databases import SettingsStorage
from util.emojis import Emojis

class ChannelCheckEvent(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.storage = SettingsStorage()

    
    PUBLIC_EXEMPT_COMMANDS = {
        "help", "invite"
    }

    
    ADMIN_EXEMPT_COMMANDS = {
        "prefix", "setprefix", "deleteprefix", "clearbot", "clearmsg", "channel"
    }

    async def is_channel_restricted(self, guild: discord.Guild, channel_id: int, member: discord.Member, command_name: str | None) -> tuple[bool, int | None]:
        
        if member.id in (self.bot.owner_ids or set()) or member.id == getattr(self.bot, "owner_id", None):
            return False, None

        try:
            if await self.bot.is_owner(member):
                return False, None
        except Exception:
            pass

       
        if member.id == guild.owner_id:
            return False, None

        
        if command_name in self.PUBLIC_EXEMPT_COMMANDS:
            return False, None

        
        if member.guild_permissions.manage_guild and command_name in self.ADMIN_EXEMPT_COMMANDS:
            return False, None

        
        allowed_channel_id = self.storage.get_allowed_channel(guild.id)
        if allowed_channel_id and channel_id != allowed_channel_id:
            return True, allowed_channel_id

        return False, None


async def setup(bot: commands.Bot):
    cog = ChannelCheckEvent(bot)
    await bot.add_cog(cog)

    @bot.before_invoke
    async def enforce_channel_restriction(ctx: commands.Context):
        if not ctx.guild or not isinstance(ctx.author, discord.Member):
            return

        cmd_name = ctx.command.root_parent.name if ctx.command.root_parent else ctx.command.name

        is_blocked, allowed_channel_id = await cog.is_channel_restricted(
            ctx.guild, ctx.channel.id, ctx.author, cmd_name
        )

        if is_blocked:
            allowed_channel = ctx.guild.get_channel(allowed_channel_id)
            channel_mention = allowed_channel.mention if allowed_channel else "the designated channel"

            embed = discord.Embed(
                description=f"{Emojis.warning} Auro commands are locked to {channel_mention}!",
                color=discord.Color.yellow()
            )

            if ctx.interaction:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                try:
                    await ctx.reply(embed=embed, delete_after=10)
                except discord.HTTPException:
                    pass

            raise commands.CheckFailure("Channel Locked")