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
    def __init__(self, bot: commands.Bot, author, version):
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
                f"{Emojis.dot} {Emojis.alien} **General Module**\n\n"
                f"{Emojis.dot} {Emojis.music_help} **Music Module**\n\n"
                f"{Emojis.dot} {Emojis.music} **Filters**\n\n"
                f"{Emojis.dot} {Emojis.playlist} **Custom Playlists**\n\n"
                f"{Emojis.dot} {Emojis.heart} **Contributors**\n\n"
            ))
            container.add_item(ui.Separator())

        elif page_name == "General":
            container = self.create_base_container(discord.Color.purple())
            container.add_item(ui.TextDisplay(
                f"## General Module {Emojis.alien}\n\n"
                f"**{Emojis.dot} </stats:1496755644823502878>**  —  View system latency\n"
                f"**{Emojis.dot} </profile:1504083683701952532>** — User information card\n"
                f"**{Emojis.dot} </clearmsg:1489274898059890841>** — Purge channel history\n"
                f"**{Emojis.dot} </contribute:1489268205171114186>** — Support development\n"
                f"**{Emojis.dot} </pic:1505107143840366654>** — Shows a user's profile picture.\n"
                f"**{Emojis.dot} </banner:1505107143840366655>** — Shows a user's profile banner.\n"
                f"**{Emojis.dot} </clearbot:1489280571283607562>** — Clean up all bot responses in the channel!\n"
                f"**{Emojis.dot} </help:1490758144677380168>** — Show this menu"
            ))
            container.add_item(ui.Separator())

        elif page_name == "Music":
            container = self.create_base_container(discord.Color.blurple())
            container.add_item(ui.TextDisplay(
                f"## Music Module {Emojis.music_help} \n\n"
                f"**{Emojis.dot} </play:1496755644823502881>** — Stream high-quality audio.\n"
                f"**{Emojis.dot} </playfromstatus:1504089125098356736>** — Play the music from your status or a friend's Spotify.\n"
                f"**{Emojis.dot} </lyrics:1502716663726866532>** — Fetch real-time song text.\n"
                f"**{Emojis.dot} stop/skip** — Stops a song \\ Skips the currently playing song .\n"
                f"**{Emojis.dot} loop/loopqueue** — Track/Queue repeat toggles.\n"
                f"**{Emojis.dot} </fix:1498209884087521382>** — Hard-reset the Auro Engine.\n"
                f"**{Emojis.dot} </radio:1499280588191043684>** — 24/7 high-quality streams.\n"
                f"**{Emojis.dot} </track_details:1500544019070058506>** — Get the details of currently playing song.\n"
                f"**{Emojis.dot} </queue_clr:1501553001641410672>** — Wipe all tracks from the current Auro Engine queue.\n"
                f"**{Emojis.dot} </queue_pop:1501553001641410673>** — Remove the last track added to the Auro Engine queue.\n"
                f"**{Emojis.dot} </queue_rmtrack:1501553001641410674>** — Remove a specific track from the queue by its name.\n"
                f"**{Emojis.dot} </queue_move:1501553001641410676>** — Move a track to a specific position in the queue.\n"
                f"**{Emojis.dot} </history:1503758516358217899>** — View the last 10 tracks played in this session.\n"
                f"**{Emojis.dot} </save:1503758516358217900>** — Sends the current song details to your DMs.\n"
            ))
            container.add_item(ui.Separator())
        elif page_name == "Filters":
            container = self.create_base_container(discord.Color.dark_gold())
            container.add_item(ui.TextDisplay(
                f"## Filters {Emojis.music}\n"
                "\n"
                "> A list of Available Filters\n\n"
                f"{Emojis.dot} </eq_bassboost:1504378844193230894> — Boost the bass frequencies.\n"
                f"{Emojis.dot} </eq_dynamic:1497979624792260612> — Balanced punch and sparkle.\n"
                f"{Emojis.dot} </eq_flat:1504378844193230895> — Flatten the equalizer settings.\n"
                f"{Emojis.dot} </eq_metal:1504378844193230896> — Enhance the mid frequencies for a metal sound.\n"
                f"{Emojis.dot} </eq_piano:1504378844193230897> — Enhance the high frequencies for a piano sound.\n"
                f"{Emojis.dot} </eq_smooth:1497979624792260613> — Warm & relaxed: Reduces sharp treble for late-night vibes.\n"
                f"{Emojis.dot} </eq_treble_boost:1504378844516323369> — Boost the high frequencies for extra sparkle.\n"
                f"{Emojis.dot} </reset:1504378844516323370> — Clear all audio filters.\n"
            ))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                f"## Custom Eq Setup {Emojis.waves} \n\n"
                f"{Emojis.dot} </seteq:1504378844516323371> — Manually tune the Auro Engine frequency bands.\n"
                "\n"
                "> Format: 'band:gain' (e.g., '0:0.25 1:0.15')\n\n"
                f"{Emojis.dot} </eq_help:1504378844516323372> — Guide for the Auro Engine frequency bands.\n"
            ))
            container.add_item(ui.Separator())
        elif page_name == "Custom Playlists":
            container = self.create_base_container(discord.Color.dark_orange())
            container.add_item(ui.TextDisplay(
                f"## Custom Playlist {Emojis.playlist}\n"
                "\n"
                f"**{Emojis.dot} </myplaylist save:1506536337975676989>** — Save or add tracks to your personal database.\n"
                f"**{Emojis.dot} </myplaylist load:1506536337975676989>** — Load a saved database playlist into the queue.\n"
                f"**{Emojis.dot} </myplaylist delete:1506536337975676989>** — Permanently delete a saved database playlist.\n"
                f"**{Emojis.dot} </myplaylist list:1506536337975676989>** — List all your saved database playlists."
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
            discord.SelectOption(label="Filters",emoji=Emojis.music,description="See the Filters."),
            discord.SelectOption(label="Custom Playlists", emoji= Emojis.playlist, description="Personal database playlist management."),
            discord.SelectOption(label="Contributors",emoji=Emojis.heart, description="See the Contributors behind me")
        ]
        super().__init__(placeholder="Select a Cog to view info...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        view: HelpLayoutView = self.view
        view.show_page(self.values[0])
        await interaction.response.edit_message(view=view)

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="help", aliases=["h"], description="💝 View the Auro command directory.")
    @commands.guild_only()
    async def help(self, ctx: commands.Context):
        version = await get_latest_version()
        view = HelpLayoutView(self.bot, ctx.author, version)
        view.message = await ctx.reply(content=None, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))