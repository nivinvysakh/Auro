import discord
import asyncio
from discord.ext import commands
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class RewindConfirmView(discord.ui.View):
    def __init__(self, ctx: commands.Context, player: Player, previous_track, current_playing_track=None):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.player = player
        self.previous_track = previous_track
        self.current_playing_track = current_playing_track
        self.value = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                f"╮(￣ω￣;)╭ Only {self.ctx.author.display_name} can confirm this action.",
                ephemeral=True
            )
            return False
        return True

    async def delay_delete(self, interaction: discord.Interaction):
        await asyncio.sleep(5)
        try:
            await interaction.delete_original_response()
        except Exception:
            pass

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.secondary, emoji=Emojis.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

        if self.player.is_playing:
            if len(self.player.history) >= 2:
                _ = self.player.history.pop()  
                _ = self.player.history.pop()  
                if self.current_playing_track:
                    self.player.queue.put_at_front(self.current_playing_track)
        else:
            if len(self.player.history) >= 1:
                _ = self.player.history.pop()

        self.player.loop = False
        await self.player.music_cache.clear_guild_cache(self.ctx.guild.id)
        await self.player.play(self.previous_track)

        embed = discord.Embed(
            description=f"⏪ **Rewinding playback to:** **{self.player.music_cache.clean_track_title(self.previous_track.title) if hasattr(self.player.music_cache, 'clean_track_title') else self.previous_track.title}**",
            color=discord.Color.blurple()
        ).set_footer(text=f"Requested by {self.ctx.author.display_name} • Self-destructing in 5s...")
        
        for child in self.children:
            child.disabled = True
            
        await interaction.edit_original_response(embed=embed, view=self)
        asyncio.create_task(self.delay_delete(interaction))

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary, emoji=Emojis.error)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        
        embed = discord.Embed(
            description="❌ Rewind action cancelled. Playback remains unchanged. (Deleting in 5s...)",
            color=discord.Color.red()
        )
        
        for child in self.children:
            child.disabled = True
            
        await interaction.response.edit_message(embed=embed, view=self)
        asyncio.create_task(self.delay_delete(interaction))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            embed = discord.Embed(
                description="⏱️ Rewind prompt timed out. No changes made. (Deleting in 5s...)",
                color=discord.Color.orange()
            )
            msg = await self.ctx.interaction.edit_original_response(embed=embed, view=self)
            await asyncio.sleep(5)
            await msg.delete()
        except Exception:
            pass


class Rewind(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="rewind",
        aliases=["previous", "prev", "back"],
        description="⏪ Replay the track that just finished playing."
    )
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rewind(self, ctx: commands.Context):
        player = cast(Player, ctx.voice_client)
        
        if not player:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{Emojis.warning} I am not active in a voice channel right now.",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )
            
        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"╮(￣ω￣;)╭ You're not in my channel!",
                    color=discord.Color.yellow()
                ),
                delete_after=10
            )

        current_playing_track = None
        if player.is_playing:
            if len(player.history) < 2:
                return await ctx.reply(
                    embed=discord.Embed(
                        description=f"{Emojis.warning} No previous track found in Auro's history cache!",
                        color=discord.Color.yellow()
                    ),
                    delete_after=10
                )
            current_playing_track = player.history[-1]
            previous_track = player.history[-2]
        else:
            if len(player.history) < 1:
                return await ctx.reply(
                    embed=discord.Embed(
                        description=f"{Emojis.warning} No previous track found in Auro's history cache!",
                        color=discord.Color.yellow()
                    ),
                    delete_after=10
                )
            previous_track = player.history[-1]

        prompt_embed = discord.Embed(
            title="Confirm Rewind",
            description=f"Are you sure you want to stop current playback and rewind to:\n**{previous_track.title}**?",
            color=discord.Color.blue()
        )
        
        view = RewindConfirmView(ctx, player, previous_track, current_playing_track)
        await ctx.reply(embed=prompt_embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rewind(bot))