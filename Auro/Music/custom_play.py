import discord
from discord.ext import commands
from discord import app_commands
from util.emojis import Emojis
from Auro.Music.play import Player
from typing import cast

class CustomPlay(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @app_commands.command(
        name="custom_play",
        description="✨ Play a local audio file."
    )
    @app_commands.guild_only()
    @app_commands.describe(
        file="🔗 The audio file you want to play (mp3, wav, flac, etc.)"
    )
    @commands.cooldown(1,30,commands.BucketType.guild)
    async def custom(self,interaction : discord.Interaction , file : discord.Attachment ):
        await interaction.response.defer()
        ALLOWED_EXTENSIONS = ('mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac')
        if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{Emojis.warning} File Not Supported.",
                    description=f"{file.filename} is not a supported audio format.",
                    color=discord.Color.yellow()
                ),
                ephemeral=True
            )
        if not interaction.user.voice:
            return await interaction.followup.send(
                embed=discord.Embed(
                    description=f"{Emojis.warning} Join a VC first!",
                    color= discord.Color.orange()
                ),
                ephemeral=True
            )
        if interaction.guild.voice_client:
            if interaction.user.voice.channel != interaction.guild.voice_client.channel:
                return await interaction.followup.send(
                    embed=discord.Embed(
                        description=f"╮(￣ω￣;)╭ You're not in {interaction.guild.voice_client.channel.mention}!",
                        color=discord.Color.yellow()
                    ), ephemeral=True
                )
        if not interaction.guild.voice_client:
            player = cast(Player, await interaction.user.voice.channel.connect(cls=Player))
        else:
             player = cast(Player, interaction.guild.voice_client)
        if player.is_playing:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{Emojis.error} Custom play not possible.",
                    description="╮(￣ω￣;)╭ I'm already playing something! Please wait for the current track to finish.",
                    color= discord.Color.red()
                )
            )
        try :
            await player.channel.edit(status=None)
            result = await player.get_tracks(file.url)
            if not result:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title=f"{Emojis.warning} ╮(￣ω￣;)╭ I'm sorry, but my server couldn't process this file!",
                        color= discord.Color.red()
                    ), ephemeral= True
                )
            track = result[0]
            track.title = "Auro Custom Play"
            track.author = interaction.user.name
            await player.play(track)
            await player.channel.edit(status=f"{Emojis.alien} Auro Custom Play ..")
            display_title = track.title if track.title != "Unknown title" else file.filename
            succes_embed = discord.Embed(
                title=f"{Emojis.alien} Custom Play Loaded",
                description=f"**Playing:** `{display_title}`\n**Size:** `{file.size // 1024} KB`",
                color= discord.Color.green()
            )
            succes_embed.set_footer(text=f"Auro Engine v1.0.0 • Custom Play")
            succes_embed.set_thumbnail(url=self.bot.user.avatar.url)

            await interaction.followup.send(
                embed=succes_embed,
            )
        except Exception as e :
            return print(f"AURO CUSTOM FILE ERROR : {e}")

async def setup(bot):
    await bot.add_cog(CustomPlay(bot))