import discord
import pomice
from discord import app_commands
from discord.ext import commands
from util.emojis import Emojis


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    async def process_pomice_errors(self, ctx_or_interaction, error) -> bool:
        
        original_error = error
        
        
        while hasattr(original_error, "original"):
            original_error = original_error.original

        
        if isinstance(original_error, pomice.exceptions.NoNodesAvailable):
            embed = discord.Embed(
                title=f"{Emojis.error} Audio Core Offline",
                description=(
                        "I am currently unable to connect to our audio nodes. `(｡•́︿•̀｡)`\n\n"
                        "**Please try again in a few moments.**"),
                color=discord.Color.red(),
            )

            
            if isinstance(ctx_or_interaction, discord.Interaction):
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                if ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await ctx_or_interaction.response.send_message(embed=embed, ephemeral=True)
            
           
            else:
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                try:
                    await ctx_or_interaction.reply(embed=embed, delete_after=10)
                except discord.HTTPException:
                    await ctx_or_interaction.send(embed=embed, delete_after=10)
            return True
            
        return False

    # normal commands errors routes to on_command_error
    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if await self.process_pomice_errors(ctx, error):
            return

        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title=f"{Emojis.cooldown} Command on Cooldown",
                description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
                color=discord.Color.orange(),
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title=f"{Emojis.error} Missing Argument",
                description=f"Usage: `{ctx.prefix}{ctx.command} {ctx.command.signature}`",
                color=discord.Color.red(),
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
        
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title=f"{Emojis.error} Bad Argument",
                description=str(error),
                color=discord.Color.red(),
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)

        elif isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        
        else:
            embed = discord.Embed(
                title=f"{Emojis.error} An Error Occurred",
                description="An unexpected error occurred while processing your command.",
                color=discord.Color.red(),
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=embed, delete_after=5)
            print(f"Text Error in command '{ctx.command}': {error}")

    # app_command Error Handel (app_command errors routes to on_app_command_error)
    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if await self.process_pomice_errors(interaction, error):
            return

        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title=f"{Emojis.cooldown} Command on Cooldown",
                description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
                color=discord.Color.orange(),
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title=f"{Emojis.error} Missing Permissions",
                description="You do not have the required permissions to run this command.",
                color=discord.Color.red(),
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cmd_name = interaction.command.name if interaction.command else "Unknown"
        print(f"Slash Error in command '{cmd_name}': {error}")
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if not interaction.message or interaction.message.id not in self.bot._connection._view_store._views:
                embed = discord.Embed(
                    title=f"{Emojis.error} Interaction Expired",
                    description=(
                                    "This button belongs to an older session and has expired.\n\n"
                                    "Please run the command again to get a fresh menu!"
                    ),
                    color= discord.Color.yellow()
                ).set_thumbnail(url=self.bot.user.avatar.url)
                try :
                    if not interaction.response.is_done():
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                except discord.HTTPException:
                    pass


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ErrorHandler(bot))
