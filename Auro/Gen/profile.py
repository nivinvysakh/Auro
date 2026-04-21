import discord
from discord.ext import commands
from util.emojis import Emojis as emojis, ButtonEmojis, BadgesIcon, UserStautsEmo
from databases import BadgesDatabase
from discord import app_commands


class ProfileButtons(discord.ui.View):
    def __init__(self, target_user, command_owner, bot):
        super().__init__(timeout=60)
        self.target = target_user
        self.command_owner = command_owner
        self.bot = bot
        self.badges_db = BadgesDatabase()
        self.message = None

        self.badge_mapping = {
            "Developer": BadgesIcon.developer,
            "Staff": BadgesIcon.staff,
            "Friend": BadgesIcon.friend,
            "Beta_Tester": BadgesIcon.beta_tester,
            "Contributor": BadgesIcon.contributor,
        }

    async def apply_tiered_theme(self, embed: discord.Embed, page_type: str):
        is_owner = await self.bot.is_owner(self.target)
        badges = await self.badges_db.get_badges(self.target.id)

        if is_owner:
            embed.color = discord.Color.red()
            embed.title = (
                f"{self.target.name}'s {page_type.title()} [{BadgesIcon.developer}]"
            )
            embed.set_author(
                name="eco.plse",
                icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQeX-ZBv4hBS5RnULagS2YA7gMBgb0p_lCc9g&s",
            )
            gifs = {
                "overview": "https://i.pinimg.com/originals/7b/b9/ed/7bb9ed00d54da2404408d685534a36d4.gif",
                "status": "https://i.pinimg.com/originals/47/ff/22/47ff225d6df531b371221b6bbbef6928.gif",
                "account": "https://i.pinimg.com/originals/6a/23/30/6a2330e2ed77ec9df2075b222e5aa87f.gif",
                "badges": "https://i.pinimg.com/originals/33/ed/e3/33ede3813b49035b5dc3e1044b8d47fa.gif",
            }
            embed.set_image(url=gifs.get(page_type, gifs["overview"]))
        elif "Staff" in badges:
            embed.title = (
                f"{self.target.name}'s {page_type.title()} [{BadgesIcon.staff}]"
            )
            embed.color = discord.Color.blue()
            embed.set_image(url="https://giffiles.alphacoders.com/132/13241.gif")
        elif "Friend" in badges:
            embed.color = discord.Color.from_str("#FF69B4")
            embed.title = (
                f"{self.target.name}'s {page_type.title()} [{BadgesIcon.friend}]"
            )
            embed.set_image(
                url="https://i.pinimg.com/originals/0f/1b/a3/0f1ba3323de4711a314119a80205c0bf.gif"
            )
        elif "Beta_Tester" in badges:
            embed.color = discord.Color.green()
            embed.title = (
                f"{self.target.name}'s {page_type.title()} [{BadgesIcon.beta_tester}]"
            )
            embed.set_image(
                url="https://i.pinimg.com/originals/71/5c/58/715c585f6a62f0869de90fa244aa80d8.gif"
            )
        elif "Contributor" in badges:
            embed.color = discord.Color.from_str("#FF8C00")
            embed.title = (
                f"{self.target.name}'s {page_type.title()} [{BadgesIcon.contributor}]"
            )
            embed.set_image(
                url="https://i.pinimg.com/originals/00/a2/0a/00a20a67bc0bdbdb698ed0ee7a1cd5db.gif"
            )

        else:
            embed.color = emojis.color
            bot_user = await self.bot.fetch_user(self.bot.user.id)
            embed.set_image(url=bot_user.banner.url)
            embed.color = discord.Color.blurple()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.command_owner.id:
            await interaction.response.send_message(
                f"{emojis.error} Only {self.command_owner.name} can interact!",
                ephemeral=True,
            )
            return False
        return True

    async def handle_button_state(
        self, interaction: discord.Interaction, clicked_button: discord.ui.Button
    ):

        await interaction.response.defer()
        for button in self.children:
            if isinstance(button, discord.ui.Button):
                button.style = discord.ButtonStyle.secondary
                button.disabled = False

        clicked_button.style = discord.ButtonStyle.success
        clicked_button.disabled = True
        return True

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    def memberstatemoji(self, member):
        stats = {
            discord.Status.online: f"{UserStautsEmo.online} | **Online**",
            discord.Status.idle: f"{UserStautsEmo.idle} | **Idle**",
            discord.Status.dnd: f"{UserStautsEmo.dnd} | **Do Not Disturb**",
            discord.Status.offline: f"{UserStautsEmo.offline} | **Offline**",
        }
        return stats.get(member.status, f"{UserStautsEmo.offline} | **Offline**")

    def get_member_devices(self, member):
        if member.web_status != discord.Status.offline:
            return "Web"
        if member.desktop_status != discord.Status.offline:
            return "Desktop"
        if member.mobile_status != discord.Status.offline:
            return "Mobile"
        return "N/A"

    @discord.ui.button(
        label="Status", style=discord.ButtonStyle.secondary, emoji=ButtonEmojis.status
    )
    async def status_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_button_state(interaction, button)
        member = interaction.guild.get_member(self.target.id)

        embed = discord.Embed()
        embed.add_field(
            name="Status",
            value=self.memberstatemoji(member) if member else "Offline",
            inline=True,
        )
        embed.add_field(
            name=f"{emojis.devicesicon} Device",
            value=f"`{self.get_member_devices(member) if member else 'N/A'}`",
            inline=True,
        )
        embed.set_thumbnail(url=self.target.display_avatar.url)

        if member and member.activity:
            if isinstance(member.activity, discord.Spotify):
                embed.add_field(
                    name=f"{emojis.spotify} Spotify",
                    value=f"> {emojis.musicplaying} \u2001 *{member.activity.title}*",
                    inline=False,
                )
                embed.set_thumbnail(url=member.activity.album_cover_url)
            else:
                embed.add_field(
                    name=f"{emojis.activity} Activity",
                    value=f"> *{member.activity.name}*",
                    inline=False,
                )

        await self.apply_tiered_theme(embed, "status")
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(
        label="Account", style=discord.ButtonStyle.secondary, emoji=ButtonEmojis.account
    )
    async def account_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_button_state(interaction, button)
        member = interaction.guild.get_member(self.target.id)

        embed = discord.Embed().set_thumbnail(url=self.target.display_avatar.url)
        embed.add_field(
            name=f"{emojis.time} Created",
            value=f"<t:{int(self.target.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name=f"{emojis.join} Joined",
            value=f"<t:{int(member.joined_at.timestamp())}:R>" if member else "N/A",
            inline=True,
        )
        embed.add_field(
            name=f"{emojis.mutual} Mutuals",
            value=f"`{len(self.target.mutual_guilds)}`",
            inline=True,
        )
        embed.add_field(
            name=f"{emojis.id} ID", value=f"`{self.target.id}`", inline=True
        )

        if member:
            embed.add_field(
                name=f"{emojis.boost} Booster",
                value=(
                    f"{emojis.success}" if member.premium_since else f"{emojis.error}"
                ),
                inline=True,
            )
            embed.add_field(
                name=f"{emojis.roles} Roles",
                value=f"`{len(member.roles) - 1}`",
                inline=True,
            )

        await self.apply_tiered_theme(embed, "account")
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(
        label="Badges", style=discord.ButtonStyle.secondary, emoji=ButtonEmojis.badges
    )
    async def badges_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_button_state(interaction, button)
        badges = await self.badges_db.get_badges(self.target.id)

        embed = discord.Embed().set_thumbnail(url=self.target.display_avatar.url)
        if badges:
            display = "\n".join(
                [
                    f"{emojis.dot} **{b.replace('_', ' ')}** | {self.badge_mapping.get(b, '🏅')}"
                    for b in badges
                ]
            )
            embed.add_field(name="Global Badges", value=display, inline=False)
        else:
            embed.description = f"{emojis.error} *No badges earned yet!*"

        await self.apply_tiered_theme(embed, "badges")
        await interaction.edit_original_response(embed=embed, view=self)


class Profile(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.hybrid_command(
        name="profile", description="🧔 View a user profile ", aliases=["pr"]
    )
    @app_commands.describe(user="✨ The user to view the profile of (optional)")
    async def profile(self, ctx: commands.Context, user: discord.User = None):
        target_user = user or ctx.author
        if target_user.bot:
            return await ctx.reply(f"{emojis.error} I cannot show profiles for bots!")

        view = ProfileButtons(target_user, ctx.author, self.bot)

        embed = discord.Embed(title=f"Overview of `{target_user.name}`")
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.add_field(
            name=f"{emojis.id} ID", value=f"`{target_user.id}`", inline=True
        )
        embed.add_field(
            name=f"{emojis.heart} Name",
            value=f"*{target_user.global_name or target_user.name}*",
            inline=True,
        )

        member = ctx.guild.get_member(target_user.id)
        nickname = (
            f"*{member.nick}*" if member and member.nick else f"{emojis.error} None"
        )
        embed.add_field(
            name=f"{emojis.nickname_emoji} Nickname", value=nickname, inline=True
        )

        await view.apply_tiered_theme(embed, "overview")
        msg = await ctx.reply(embed=embed, view=view)
        view.message = msg


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Profile(bot))
