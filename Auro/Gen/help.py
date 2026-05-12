import discord
from discord import ui
from discord.ext import commands
from util.emojis import Emojis, ButtonEmojis , BadgesIcon
import aiohttp

async def get_latest_version():
    url = "https://api.github.com/repos/ilynivin/Auro/releases/latest"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("tag_name", "Unknown")
            return "v1.0.0"

class HelpLayoutView(ui.LayoutView):
    def __init__(self, bot, author, version):
        super().__init__(timeout=300) 
        self.bot = bot
        self.author = author
        self.version = version
        self.bot_icon = bot.user.display_avatar.url
        self.message = None 
        self.show_page("Home")

    def create_base_container(self, color):
        container = ui.Container(accent_color=color)
        container.add_item(ui.Section(
            ui.TextDisplay(f"# Auro 🌛 \n*A high-fidelity music engine for Discord.*\n > This menu Expires in 5 Minutes."),
            accessory=ui.Thumbnail(self.bot_icon)
        ))
        container.add_item(ui.Separator())
        return container

    def show_page(self, page_name):
        self.clear_items()
        
        if page_name == "Home":
            container = self.create_base_container(discord.Color.gold())
            container.add_item(ui.TextDisplay(
                f"### Welcome to Auro {self.version}\n"
                f"Crystal-clear audio, live synced lyrics, and cinematic filters.\n\n"
                f"**Modules Available:**\n\n"
                f"{Emojis.dot} {Emojis.alien} **General Module**\n"
                f"{Emojis.dot} {Emojis.music_help} **Music Module**\n"
                f"{Emojis.dot} {Emojis.heart} **Contributors**\n"
            ))
            container.add_item(ui.Separator())

        elif page_name == "General":
            container = self.create_base_container(discord.Color.purple())
            container.add_item(ui.TextDisplay(
                f"## {Emojis.alien} General Module\n\n"
                f"**{Emojis.dot} status** — View system latency\n"
                f"**{Emojis.dot} profile** — User information card\n"
                f"**{Emojis.dot} clearmsg** — Purge channel history\n"
                f"**{Emojis.dot} contribute** — Support development\n"
                f"**{Emojis.dot} clearbot** — Clean up all bot responses in the channel!\n"
                f"**{Emojis.dot} help** — Show this menu"
            ))
            container.add_item(ui.Separator())

        elif page_name == "Music":
            container = self.create_base_container(discord.Color.blurple())
            container.add_item(ui.TextDisplay(
                f"## {Emojis.music_help} Music Module\n\n"
                f"**{Emojis.dot} play** — Stream high-quality audio\n"
                f"**{Emojis.dot} lyrics** — Fetch real-time song text\n"
                f"**{Emojis.dot} filters** — Audio enhancement toggles\n"
                f"**{Emojis.dot} stop/skip** — Queue control\n"
                f"**{Emojis.dot} loop/loopqueue** — Track/Queue repeat toggles\n"
                f"**{Emojis.dot} Fix** — Hard-reset the Auro Engine\n"
                f"**{Emojis.dot} Radio** — 24/7 high-quality streams\n"
                f"**{Emojis.dot} track_details** — Get the details of currently playing song.\n"
                f"**{Emojis.dot} queue_clr** — Wipe all tracks from the current Auro Engine queue.\n"
                f"**{Emojis.dot} queue_pop** — Remove the last track added to the Auro Engine queue.\n"
                f"**{Emojis.dot} queue_rmtrack** — Remove a specific track from the queue by its name.\n"
                f"**{Emojis.dot} queue_move** — Move a track to a specific position in the queue.\n"
                f"**{Emojis.dot} history** — View the last 10 tracks played in this session.\n"
                f"**{Emojis.dot} save** — Sends the current song details to your DMs.\n"
            ))
            container.add_item(ui.Separator())
        elif page_name == "Contributors":
            container = self.create_base_container(discord.Color.red())
            container.add_item(ui.TextDisplay(
                f"## {Emojis.star_animate} Open Source project.\n"
                "Auro is a community-driven project. Our source code is public and open for contributions.\n"
                "**GitHub:** [ilynivin/Auro](https://github.com/ilynivin/Auro)"
            ))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                f"### {Emojis.heart} Join the Project\n"
                f"**Lead Maintainer:** `eclipse`\n"
                "We welcome Pull Requests! Whether it's fixing a loop cache bug or optimizing Lavalink nodes, your help makes Auro better."
            ))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                "### 📜 License AGPLv3\n"
                "Auro is licensed under the **GNU Affero General Public License v3**.\n"
                "* **Copyleft:** Any modifications hosted publicly must also be open-sourced.\n"
                "* **Freedom:** You are free to study, change, and distribute the code."
            ))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                "### ✨ Wall of Fame\n"
                "Check out our [Contributors Registry](https://github.com/ilynivin/Auro/blob/Main/contributors.md) "
                "to see the legends helping Auro grow.\n\n"
                "*Every pull request, bug report, and logic fix helps us reach audio perfection.*"
            ))
            container.add_item(ui.Separator())
            invisible_space = "\u2800"
            container.add_item(ui.TextDisplay(
                f"{invisible_space * 22} **<————— x —————>**"
            ))
        
        self.add_item(container)

        select_row = ui.ActionRow()
        select_row.add_item(ModuleSelector())
        self.add_item(select_row)

        button_row = ui.ActionRow()
        button_row.add_item(ui.Button(label="Github", url="https://github.com/ilynivin/Auro", style=discord.ButtonStyle.link, emoji=ButtonEmojis.github))
        button_row.add_item(ui.Button(label="Support", url="https://discord.gg/gRJjC3H6aA", style=discord.ButtonStyle.link, emoji=ButtonEmojis.server))
        self.add_item(button_row)

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except (discord.HTTPException, discord.Forbidden, discord.NotFound):
                pass
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message(f"{Emojis.error} This menu is managed by the command author.", ephemeral=True)
            return False
        return True

class ModuleSelector(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Home", emoji=ButtonEmojis.home, description="Go back to the overview"),
            discord.SelectOption(label="General", emoji=Emojis.alien, description="Utility and system commands"),
            discord.SelectOption(label="Music", emoji=Emojis.music_help, description="Audio engine and queue commands"),
            discord.SelectOption(label="Contributors",emoji=Emojis.heart, description="See the Contributors behind me")
        ]
        super().__init__(placeholder="Select a Cog to view info...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        view: HelpLayoutView = self.view
        view.show_page(self.values[0])
        await interaction.response.edit_message(view=view)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", aliases=["h"], description="💝 View the Auro command directory.")
    @commands.guild_only()
    async def help(self, ctx: commands.Context):
        version = await get_latest_version()
        view = HelpLayoutView(self.bot, ctx.author, version)
        view.message = await ctx.reply(content=None, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))