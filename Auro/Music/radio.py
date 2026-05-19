import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import cast
from Auro.Music.play import Player
from util.emojis import Emojis

class Radio(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.stations = {
            "lofi": "https://streams.fluxfm.de/Chillhop/mp3-128/streams.fluxfm.de/",
            "synthwave": "https://stream.nightride.fm/nightride.m4a"
        }

    @app_commands.command(name="radio", description="📻 Tune into stable, 24/7 high-quality streams.")
    @app_commands.describe(genre="Pick your vibe")
    @app_commands.choices(genre=[
        app_commands.Choice(name="Lofi Chills 🌙", value="lofi"),
        app_commands.Choice(name="Synthwave Night 🚗", value="synthwave")
    ])
    async def radio(self, interaction: discord.Interaction, genre: app_commands.Choice[str]):
        lock = self.bot.get_cog("Stopvc")
        if lock and lock.maintenance_lock:
            return await interaction.response.send_message(
                content=f"{Emojis.warning} **Auro Maintenance:** New sessions are currently locked by the developer. [dev]",ephemeral=True
            )
        if not interaction.user.voice:
            return await interaction.response.send_message(f"{Emojis.error} You need to be in a voice channel!", ephemeral=True)
        
        if interaction.guild.voice_client and interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message(
                f"{Emojis.error} I'm already playing in {interaction.guild.voice_client.channel.mention}!", 
                ephemeral=True
            )

        await interaction.response.defer()

        if not interaction.guild.voice_client:
            player: Player = await interaction.user.voice.channel.connect(cls=Player)
        else:
            player: Player = cast(Player, interaction.guild.voice_client)
        if player.current and player.is_playing:
            if player.music_cache:
                guild_id = interaction.guild.id
                await player.music_cache.clear_all_guild_cache(guild_id)
                player.loop = False
                player.loop_queue = False
                await player.stop()
            
        try:
            player.queue.clear()
            results = await player.node.get_tracks(self.stations[genre.value])

            if not results:
                return await interaction.followup.send(f"{Emojis.error} Station currently unreachable.")

            track = results[0]
            track.title = f"Auro Radio: {genre.name}"
            track.author = "Nightride FM"
            await player.channel.edit(status=None)
            await asyncio.sleep(3)
            try:
                await player.channel.edit(status=f"📻 Tuning: **{genre.name}**")
            except:
                pass
            await player.play(track)
            await player.set_volume(0)

            embed = discord.Embed(
                title=f"📻 {track.title}",
                description=f"Connecting to stream... Audio will start in 2s.",
                color=discord.Color.dark_purple()
            )
            embed.set_footer(text="Auro Engine • Radio")
            msg = await interaction.followup.send(embed=embed)

            await asyncio.sleep(2)
            await player.set_volume(100)
            done_embed = discord.Embed(
                title=f"📻 {track.title}",
                description=f"{Emojis.success} **Stream is now live.** Enjoy the music!",
                color=discord.Color.green()
            ).set_footer(text="Auro Engine • Radio")
            await msg.edit(embed=done_embed)

        except Exception as e:
            await interaction.followup.send(f"{Emojis.error} Connection failed. Please try again.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Radio(bot))