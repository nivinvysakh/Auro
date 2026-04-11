import discord
from discord.ext import commands
from databases import BadgesDatabase
from util.emojis import Emojis as _Emojis
from util.emojis import BadgesIcon


class Badges(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.badges_db = BadgesDatabase()
        self.badges = ["Developer", "Staff", "Friend", "Beta_Tester", "Contributor"]

    async def async_setup(self):
        await self.badges_db.init_db()

    @commands.command(name="addbadge", aliases=["addbadges", "givebadge", "adbadge"])
    @commands.is_owner()
    async def add_badge_command(
        self, ctx: commands.Context, User: discord.User = None, badge: str = None
    ):
        """Add a Badge to a User"""
        if User is None or badge is None:
            await ctx.reply(
                f"Missing required arguments. Usage: `addbadge <user> <badge>`",
                delete_after=3,
            )
            return True

        if badge not in self.badges:
            embed = discord.Embed(
                title="Invalid Badge",
                description=f"{_Emojis.error} The badge '{badge}' is not a valid badge. \n **Valid badges are:** \n {_Emojis.dot} Developer\n {_Emojis.dot} Staff\n {_Emojis.dot} Friend\n {_Emojis.dot} Beta_Tester\n {_Emojis.dot} Contributor ",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed, delete_after=10)
            return True
        try:
            await self.badges_db.add_badge(User.id, badge)
            await ctx.reply(f"> {_Emojis.success} Added badge {badge} to {User.name}")
            print(f"Badge Added to {User.global_name} - > {badge}")
        except Exception as e:
            await ctx.reply(f"Error adding badge: {e}")

    async def get_badges(self, user_id: int) -> list:
        badges = await self.badges_db.get_badges(user_id)
        return badges if badges else []

    @commands.command(name="showbadges", aliases=["badges", "badge"])
    @commands.is_owner()
    async def show_badge(self, ctx: commands.Context, User: discord.User = None):
        """Show Badges of a User"""
        if User is None:
            User = ctx.author
        badges = await self.get_badges(User.id)
        if not badges:
            no_badges_embed = discord.Embed(
                title=f"{User.name} has no badges",
                description=f"{_Emojis.error} This user does not have any badges.",
                color=discord.Color.red(),
            ).set_thumbnail(url=User.avatar.url if User.avatar else None)
            await ctx.reply(embed=no_badges_embed, delete_after=30)
            return True
        badges_str = "\n".join(f"{_Emojis.dot} {badge}" for badge in badges)
        badges_embed = (
            discord.Embed(
                title=f"{User.name}'s Badges [{BadgesIcon.developer}]",
                description=badges_str,
                color=discord.Color.green(),
            )
            .set_thumbnail(url=User.avatar.url if User.avatar else None)
            .set_footer(text=f"Total Badges: {len(badges)}")
        )
        await ctx.reply(embed=badges_embed, delete_after=30)
        return True

    @commands.command(
        name="delbadges", aliases=["removebadge", "removebadges", "delbadge"]
    )
    @commands.is_owner()
    async def del_badges(
        self, ctx: commands.Context, User: discord.User = None, badge: str = None
    ):

        if User is None or badge is None:
            await ctx.reply(
                f"> Missing required arguments. Usage: `delbadges <user> <badge>`",
                delete_after=3,
            )
            return True

        badges = await self.get_badges(User.id)
        if not badges:
            await ctx.reply(f"{User.name} does not have any badges")
            return True

        if badge not in badges:
            await ctx.reply(f"{User.name} does not have the badge: {badge}")
            return True

        try:
            await self.badges_db.remove_badge(User.id, badge)
            await ctx.reply(
                f" {_Emojis.success} Removed badge {badge} from {User.name}",
                delete_after=5,
            )
        except Exception as e:
            await ctx.reply(f"Error removing badge: {e}")
        return True


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Badges(bot))
