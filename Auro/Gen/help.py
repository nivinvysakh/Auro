import discord
from discord.ext import commands
from util.emojis import Emojis, ButtonEmojis
import aiohttp


async def get_latest_version():
    url = "https://api.github.com/repos/ilynivin/Auro/releases/latest"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("tag_name", "Unknown")
            return "v1.0.0"

class HelpView(discord.ui.View):
    def __init__(self, bot, author, version):
        super().__init__(timeout=60)
        self.bot = bot
        self.author = author
        self.version = version
        self.current_page = 1
        self.message = None
        self.add_item(
            discord.ui.Button(
                label="Github_Link",
                url="https://github.com/ilynivin/Auro",
                style=discord.ButtonStyle.link,
                emoji=ButtonEmojis.github,
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Server_link",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/gRJjC3H6aA",
                emoji=ButtonEmojis.server,
            )
        )

    def create_embed(self):
        embed = discord.Embed(
            color=discord.Color.blurple(), title=f"{Emojis.auro} Auro Infrastructure"
        )
        embed.set_image(url="https://i.pinimg.com/originals/5a/24/39/5a24398389aacad9095f240abeca30b8.gif")
        embed.set_footer(
            text=f"Auro {self.version} | Page {self.current_page}/2",
            icon_url=self.bot.user.avatar.url,
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        if self.current_page == 1:
            embed.add_field(
                name="📁 General Module",
                value=(
                    f"**{Emojis.dot} status** — View system latency\n"
                    f"**{Emojis.dot} profile** — User information card\n"
                    f"**{Emojis.dot} clearmsg** — Purge channel history\n"
                    f"**{Emojis.dot} contribute** — Support development\n"
                    f"**{Emojis.dot} help** — Show this menu"
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="🎵 Music Module",
                value=(
                    f"**{Emojis.dot} play** — Stream high-quality audio\n"
                    f"**{Emojis.dot} lyrics** — Fetch real-time song text\n"
                    f"**{Emojis.dot} filters** — Audio enhancement toggles\n"
                    f"**{Emojis.dot} stop/skip** — Queue control\n"
                    f"**{Emojis.dot} loop/loopqueue** — Track/Queue repeat toggles\n"
                    f"**{Emojis.dot} Fix** — Hard-resets the Auro Engine to fix 'Ghost Audio' issues.\n"
                    f"**{Emojis.dot} Radio** — Tune into stable, 24/7 high-quality streams.\n"
                ),
                inline=False,
            )
        return embed

    async def on_timeout(self):

        for item in self.children:
            item.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

    @discord.ui.button(
        label="Back",
        style=discord.ButtonStyle.blurple,
        disabled=True,
        emoji=Emojis.left_arrow,
    )
    async def back_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = 1
        button.disabled = True
        self.children[1].disabled = False
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(
        label="Next", style=discord.ButtonStyle.blurple, emoji=Emojis.right_arrow
    )
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = 2
        button.disabled = True
        self.children[0].disabled = False
        await interaction.response.edit_message(embed=self.create_embed(), view=self)
    
    @discord.ui.button(
            label="delete",
            style= discord.ButtonStyle.gray,
            emoji=f"{Emojis.error}"
    )
    async def delete(self, intraction: discord.Interaction , button: discord.ui.button):
        await intraction.message.delete()
    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user != self.author:
            await interaction.response.send_message(
                "This menu is managed by the command author.", ephemeral=True
            )
            return False
        return True


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help", aliases=["h"], description="💝 View the Auro command directory."
    )
    @commands.guild_only()
    async def help(self, ctx: commands.Context):
        version = await get_latest_version()
        view = HelpView(self.bot, ctx.author , version)
        embed = view.create_embed()

        message = await ctx.reply(embed=embed, view=view)
        view.message = message


async def setup(bot):
    await bot.add_cog(Help(bot))
