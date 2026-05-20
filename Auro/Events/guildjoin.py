import discord
from discord import ui
from discord.ext import commands
from util.emojis import Emojis, ButtonEmojis

class WelcomeLayout(ui.LayoutView):
    def __init__(self, bot:commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.bot_icon = bot.user.display_avatar.url
        self.build_ui()

    def create_base_container(self, color):
        container = ui.Container(accent_color=color)
        container.add_item(ui.Section(
            ui.TextDisplay(f"# Auro 🌛 \n*A high-fidelity music engine for Discord.*"),
            accessory=ui.Thumbnail(self.bot_icon)
        ))
        container.add_item(ui.Separator())
        return container

    def build_ui(self):
        
        container = self.create_base_container(discord.Color.gold())
        container.add_item(ui.TextDisplay(
            f"### {Emojis.wave} Hola, I am Auro.\n"
            f"Crystal-clear audio and live synced lyrics for your server.\n\n"
            f"**{Emojis.dot} Getting Started:**\n"
            f"• Use `/help` or <@1486677271665184798> to view the command directory.\n"
            f"• Join a Voice Channel and use `/play`."
        ))
        container.add_item(ui.Separator())
        

        
        container.add_item(ui.TextDisplay(
            f"## {Emojis.star_animate} Open Source Project\n"
            f"Auro is built under the **AGPLv3** license. Inspect the engine [here](https://github.com/ilynivin/Auro)."
        ))
        container.add_item(ui.Separator())
        gal = ui.MediaGallery()
        gal.add_item(media="https://cdn.pfps.gg/banners/6920-anime-eyes.gif")
        container.add_item(gal)
        
        self.add_item(container)
        
        button_row = ui.ActionRow()
        
        
        button_row.add_item(ui.Button(
            label="Github", 
            url="https://github.com/ilynivin/Auro", 
            style=discord.ButtonStyle.link, 
            emoji=ButtonEmojis.github
        ))

        
        dismiss_btn = ui.Button(
            label="Dismiss", 
            style=discord.ButtonStyle.secondary, 
            emoji="🗑️"
        )
        
        
        async def dismiss_callback(interaction: discord.Interaction):
            if interaction.user.guild_permissions.manage_messages:
                await interaction.message.delete()
            else:
                await interaction.response.send_message(
                    f"{Emojis.dot} Only users with `Manage Messages` can dismiss this.", 
                    ephemeral=True
                )
        
        dismiss_btn.callback = dismiss_callback
        button_row.add_item(dismiss_btn)
        
        self.add_item(button_row)

class Guild(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.view_channel and perms.send_messages:
                view = WelcomeLayout(self.bot)
                await channel.send(content=None,view=view)
                break


async def setup(bot):
    await bot.add_cog(Guild(bot))