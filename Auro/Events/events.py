import discord
from discord.ext import commands
import asyncio
import time  
from util.emojis import Emojis
from typing import cast
from Auro.Music.play import Player
from databases.tracking import TrackingStorage  


class Inactivity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.storage = TrackingStorage()  

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
       
        player = cast(Player, member.guild.voice_client)

        # --- LIVE VOICE TRACKING MODULE ---
        if player and player.channel:
            
            if isinstance(player.channel, discord.StageChannel):
                return
            
            if not member.bot:
                
                if after.channel and after.channel.id == player.channel.id:
                    if not before.channel or before.channel.id != player.channel.id:
                        self.storage.start_session(member.id, time.time())

                
                elif before.channel and before.channel.id == player.channel.id:
                    if not after.channel or after.channel.id != player.channel.id:
                        self.storage.end_session(member.id, time.time())

            
            elif member.id == self.bot.user.id and after.channel:
        
                for human in after.channel.members:
                    if not human.bot:
                        
                        self.storage.start_session(human.id, time.time())

        # --- AUDIO AUTO-STATE INTERCEPTORS  ---
        if member.id == self.bot.user.id:
            if not player:
                return

            if before.channel and not after.channel:
                
                if before.channel:
                    
                    for human in before.channel.members:
                        if not human.bot:
                            self.storage.end_session(human.id, time.time())
                await player.destroy()
                return

            if not before.suppress and after.suppress:
                if isinstance(player.channel, discord.StageChannel):
                    if player.controller:
                        await player.controller.send(
                            f"{Emojis.warning} **Access Revoked:** Leaving Stage.",
                            delete_after=15,
                        )
                    await player.destroy()
                    return

            if not before.mute and after.mute:
                if player.is_playing and not player.is_paused:
                    await player.set_pause(True)
                    player.manual_pause = False
                    if player.controller:
                        embed = discord.Embed(
                            title=f"{Emojis.warning} **Paused:** Auro is Muted",
                            color=discord.Color.yellow(),
                        ).set_footer(
                            text="Unmute to resume",
                            icon_url=self.bot.user.display_avatar.url,
                        )
                        await player.controller.send(embed=embed, delete_after=5)
                return

            elif before.mute and not after.mute:
                if player.is_paused and not player.manual_pause:
                    await player.set_pause(False)
                    if player.controller:
                        await player.controller.send(
                            f"{Emojis.success} **Resumed:** Audio restored.",
                            delete_after=5,
                        )
                return

        # --- INACTIVITY CLEANUP  ---
        if not player or not player.channel:
            return

        if len(player.channel.members) == 1:
            await player.set_pause(True)
            await asyncio.sleep(300)
            player = cast(Player, member.guild.voice_client)
            if player and len(player.channel.members) == 1:
                if player.controller:
                    await player.controller.send(
                        embed=discord.Embed(
                            title=f"{Emojis.warning} **Disconnected:** Left voice channel due to inactivity.\n {Emojis.dot} **Reason:** No listeners detected.",
                            color=discord.Color.yellow(),
                        ).set_footer(
                            text="Auro will rejoin when you play music again.",
                            icon_url=self.bot.user.display_avatar.url,
                        )
                    )
                
                for human in player.channel.members:
                    if not human.bot:
                        self.storage.end_session(human.id, time.time())
                await player.destroy()

        else:
            if player.is_paused and not player.manual_pause and not member.guild.me.voice.mute:
                await player.set_pause(False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        mentions = (f"<@!{self.bot.user.id}>", f"<@{self.bot.user.id}>")
        if not message.content.startswith(mentions):
            return

        parts = message.content.split()
        if len(parts) < 2:
            return

        trigger = parts[1].lower()
        music_triggers = ["play", "p", "py", "pl", "stop", "stp", "dc", "leave", "getout"]

        if trigger in music_triggers:
            
            if not message.author.guild_permissions.manage_guild:
                channel_cog = self.bot.get_cog("ChannelGroup")
                if channel_cog:
                    allowed_channel_id = channel_cog.storage.get_allowed_channel(message.guild.id)
                    
                    if allowed_channel_id and message.channel.id != allowed_channel_id:
                        allowed_channel = message.guild.get_channel(allowed_channel_id)
                        if allowed_channel:
                            await message.reply(
                                embed=discord.Embed(
                                    description=f"{Emojis.warning} Auro music commands are locked to {allowed_channel.mention}!",
                                    color=discord.Color.yellow()
                                ), delete_after=10
                            )
                        return  

        ctx = await self.bot.get_context(message)
        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            return

        if trigger in ["play", "p", "py", "pl"]:
            if len(parts) >= 3:
                search_query = " ".join(parts[2:])
                if ctx.author.voice:
                    await music_cog.play.callback(music_cog, ctx, search=search_query)

        elif trigger in ["stop", "stp", "dc", "leave", "getout"]:
            if ctx.author.voice:
                await music_cog.stop.callback(music_cog, ctx)


async def setup(bot: commands.Bot):
    await bot.add_cog(Inactivity(bot))