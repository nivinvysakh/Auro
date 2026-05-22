import discord
from discord import app_commands
from discord.ext import commands
from util.emojis import Emojis
from databases.prefix import SettingsStorage

class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = SettingsStorage()
    
    # --- Auto Complete Async Function ---
    async def prefix_autocomplete(self, interaction: discord.Interaction, current: str):
        suggestions = ["a!", "!", "?", "$", "#", "p!", "m!", "audio!", "auro "]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in suggestions if current.lower() in choice.lower()

        ][:25]

    @commands.hybrid_command(name="setprefix", description="⚙️ Change Auro's command prefix for this server.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @app_commands.describe(new_prefix="✨ The new prefix symbol (e.g. !, $, p!)")
    async def setprefix(self, ctx: commands.Context, new_prefix: str):
        if len(new_prefix) > 5:
            return await ctx.reply(f"{Emojis.error} Prefix must be 5 characters or less.", delete_after=5)

        self.db.set_prefix(ctx.guild.id, new_prefix)
        
        embed = discord.Embed(
            title="⚙️ Server Configuration Updated",
            description=f"Auro's prefix for **{ctx.guild.name}** has been updated to: `{new_prefix}`\n\n*Example command usage:* `{new_prefix}play`",
            color=discord.Color.green()
        ).set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.reply(embed=embed)

    @setprefix.autocomplete('new_prefix')
    async def setprefix_autocomplete_trigger(self, interaction: discord.Interaction, current: str):
        return await self.prefix_autocomplete(interaction, current)
    
    @commands.hybrid_command(name="deleteprefix", aliases=["resetprefix"], description="🗑️ Reset Auro's prefix back to default on this server.")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def deleteprefix(self, ctx: commands.Context):
        self.db.delete_prefix(ctx.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Server Configuration Reset",
            description=f"Auro's command prefix has been reset to default: `a!`\n\n*Example command usage:* `a!play`",
            color=discord.Color.yellow()
        ).set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))