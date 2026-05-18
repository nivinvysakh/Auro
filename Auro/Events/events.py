import discord
from discord.ext import commands
import asyncio
from util.emojis import Emojis
from typing import cast
from Auro.Music.play import Player


class Inactivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):

        if member.id == self.bot.user.id:
            player = cast(Player, member.guild.voice_client)
            if not player:
                return

            if before.channel and not after.channel:
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

        player = cast(Player, member.guild.voice_client)
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
                await player.destroy()

        else:

            if player.is_paused and not player.manual_pause and not member.guild.me.voice.mute:
                await player.set_pause(False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        mentions = (f"<@!{self.bot.user.id}>", f"<@{self.bot.user.id}>")
        if not message.content.startswith(mentions):
            return

        parts = message.content.split()
        if len(parts) < 2:
            return

        ctx = await self.bot.get_context(message)
        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            return

        trigger = parts[1].lower()

        if trigger in ["play", "p", "py", "pl"]:
            if len(parts) >= 3:
                search_query = " ".join(parts[2:])
                if ctx.author.voice:
                    await music_cog.play.callback(music_cog, ctx, search=search_query)

        elif trigger in ["stop", "stp", "dc", "leave", "getout"]:
            if ctx.author.voice:
                await music_cog.stop.callback(music_cog, ctx)


async def setup(bot : commands.Bot):
    await bot.add_cog(Inactivity(bot))
