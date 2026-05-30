import discord
from discord.ext import commands
from discord import app_commands
from util.emojis import Emojis as emojis, ButtonEmojis
from databases.tracking import TrackingStorage

class ListeningSessionContext(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.storage = TrackingStorage()
        
        
        self.ctx_menu = app_commands.ContextMenu(
            name="Listening Hours",
            callback=self.view_listening_hours_callback,
            type=discord.AppCommandType.user
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    @app_commands.allowed_installs(guilds=True,users=False)
    @app_commands.allowed_contexts(guilds=True,dms=False,private_channels=False)
    async def view_listening_hours_callback(self, interaction: discord.Interaction, user: discord.User):
        
        if user.bot:
            return await interaction.response.send_message(
                f"{emojis.error} Bots cannot listen to music sessions!", 
                ephemeral=True
            )

        
        await interaction.response.defer(ephemeral=False)

        
        total_hours = self.storage.get_lifetime_hours(user.id)

       
        embed = discord.Embed(
            title=f"{emojis.session} Voice Session Analytics",
            description=f"Tracking profile stats for {user.mention}",
            color=discord.Color.blurple()
        )
        
        
        if total_hours > 0:
            embed.add_field(
                name=f"{ButtonEmojis.status} Time Listened",
                value=f"> `{total_hours}` Hours spent in VC with Auro",
                inline=False
            )
        else:
            embed.add_field(
                name=f"{ButtonEmojis.status} Time Listened",
                value=f"> {emojis.error} *No logged listening hours found yet.*",
                inline=False
            )

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(
            text=f"Auro Engine • Real-time Session Tracker", 
            icon_url=self.bot.user.display_avatar.url
        )

        
        await interaction.edit_original_response(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ListeningSessionContext(bot))