import discord
import pomice
import aiohttp
from util.emojis import Emojis , PlayerEmojis

class VolumeModel(discord.ui.Modal , title="Adjust Volume"):
    volume_input = discord.ui.TextInput(
        label="Enter Volume Percentage (0-100)",
        placeholder="eg, 80",
        min_length=1,
        max_length=100,
        required=True
    )
    def __init__(self,player : pomice.Player):
        super().__init__()
        self.player = player
    
    async def on_submit(self, interaction : discord.Interaction):
        if not self.player.channel or not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
           return await interaction.response.send_message(
               f"{Emojis.warning} You must be in my voice channel to adjust the volume.",
               ephemeral=True
           ) 
        value = self.volume_input.value.strip()
        if not value.isdigit():
            return await interaction.response.send_message(
                f"{Emojis.warning} Please enter a valid number.",
                ephemeral=True
            )
        volume = int(value)
        if volume < 0 or volume > 100:
            return await interaction.response.send_message(
                f"{Emojis.warning} Volume must be between 0 and 100",
                ephemeral=True
            )
        await self.player.set_volume(volume)
        await interaction.response.send_message(
            f"{Emojis.success} Volume adjusted to **{volume}** by {interaction.user.mention}",
            delete_after=10
        )


class NowPlayingView(discord.ui.View):
    def __init__(self, bot: discord.Client, player : pomice.Player, track: pomice.Track, format_time_func):
        super().__init__(timeout=track.length / 1000) 
        self.bot = bot
        self.player = player
        self.track = track
        self.format_time = format_time_func
        self.message = None

    async def check_voice_state(self, interaction: discord.Interaction, button: discord.ui.Button) -> bool:
        if not self.player.channel:
            button.disabled = True
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                f"{Emojis.warning} I am not connected to any voice channel.", ephemeral=True
            )
            return False

        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            await interaction.response.send_message(
                f"{Emojis.warning} You must be in my voice channel to use this button.", ephemeral=True
            )
            return False

        if not self.player.is_playing or not self.player.current or self.player.current != self.track:
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                f"{Emojis.warning} This track is no longer playing.", ephemeral=True
            )
            return False
            
        return True

    @discord.ui.button(emoji=PlayerEmojis.play, style=discord.ButtonStyle.secondary)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_voice_state(interaction, button):
            return

        if not self.player.is_paused:
            return await interaction.response.send_message(
                f"{Emojis.warning} Playback is already running.", ephemeral=True
            )

        if interaction.guild.me.voice and interaction.guild.me.voice.mute:
            return await interaction.response.send_message(
                f"{Emojis.warning} I cannot resume while **Server Muted**!", ephemeral=True
            )

        await self.player.set_pause(False)
        self.player.manual_pause = False
        await interaction.response.send_message(
            f"{Emojis.success} **Resumed** by {interaction.user.mention}", delete_after=5
        )

    @discord.ui.button(emoji=PlayerEmojis.pause, style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_voice_state(interaction, button):
            return

        if self.player.is_paused:
            return await interaction.response.send_message(
                f"{Emojis.warning} Playback is already paused.", ephemeral=True
            )

        await self.player.set_pause(True)
        self.player.manual_pause = True
        await interaction.response.send_message(
            f"{Emojis.success} **Paused** by {interaction.user.mention}", delete_after=5
        )

    @discord.ui.button(emoji=PlayerEmojis.skip, style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_voice_state(interaction, button):
            return

        if self.player.current.is_stream:
            await self.player.stop()
            try:
                await self.player.channel.edit(status=None)
            except:
                pass
            return await interaction.response.send_message(
                f"{Emojis.success} `Radio` mode switched to `Player` mode"
            )

        self.player.loop = False
        music_cog = self.bot.get_cog("Music")
        if music_cog:
            await self.player.music_cache.clear_guild_cache(interaction.guild.id)
            
        current_title = self.player.current.title
        await self.player.stop()
        await interaction.response.send_message(
            f"{Emojis.success} **Skipped:** {current_title}", delete_after=5
        )

    @discord.ui.button(emoji=PlayerEmojis.volume, style=discord.ButtonStyle.secondary)
    async def volume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.channel:
            button.disabled = True
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send(
                f"{Emojis.warning} I am not connected to any voice channel.", ephemeral=True
            )

        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            return await interaction.response.send_message(
                f"{Emojis.warning} You must be in my voice channel to use this button.", ephemeral=True
            )

        await interaction.response.send_modal(VolumeModel(self.player))

    @discord.ui.button(emoji=PlayerEmojis.stop, style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.channel:
            button.disabled = True
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send(
                f"{Emojis.warning} I am not connected to any voice channel.", ephemeral=True
            )

        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            return await interaction.response.send_message(
                f"{Emojis.warning} You must be in my voice channel to use this button.", ephemeral=True
            )

        await self.player.music_cache.clear_guild_cache(interaction.guild.id)
        await self.player.music_cache.clear_loop_queue(interaction.guild.id)

        try:
            await self.player.channel.edit(status=None)
        except:
            pass

        self.player.queue.clear()
        await self.player.destroy()

        embed = discord.Embed(
            title=f"{Emojis.success} Session Terminated",
            description=f"Playback stopped and player disconnected by {interaction.user.mention}.",
            color=discord.Color.red(),
        ).set_footer(
            text="Auro Engine • Offline", icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @discord.ui.button(emoji=PlayerEmojis.refresh, style=discord.ButtonStyle.secondary)
    async def refresh_position(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_voice_state(interaction, button):
            return
       
        source = self.track.info.get("sourceName", "Unknown").capitalize()
        
        embed = discord.Embed(
            title=f"**Now Playing** {Emojis.musicplaying}",
            description=(
                f"{Emojis.dot}  **Title** :  **{self.track.title}** \n"
                f"{Emojis.dot}  **Author** : *{self.track.author}* \n"
                f"{Emojis.dot}  **Position** : `{self.format_time(self.player.position)}` \\ `{self.format_time(self.track.length)}` \n"
                f"{Emojis.dot}  **Link** : [Watch Video]({self.track.uri})\n"
            ),
            color=discord.Color.green(),
        )
        
        embed.set_thumbnail(url=self.player.current.thumbnail)
        embed.set_footer(
            text=f"Auro Engine  |  {source}", icon_url=self.bot.user.avatar.url
        )

        if hasattr(self.track, "requester"):
            embed.add_field(
                name=f"{Emojis.star_animate} Requested by", 
                value=f"\n{self.track.requester.mention}", 
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            try:
                await self.message.edit(view=self)
            except (discord.HTTPException, aiohttp.ClientError):
                pass