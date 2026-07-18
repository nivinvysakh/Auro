import discord
from discord.ext import commands
from datetime import datetime, timezone
from Music.play import Player

class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.id != self.bot.user.id:
            return

        player = after.guild.voice_client
        if not player:
            return
        
        is_currently_timed_out = after.timed_out_until is not None and after.timed_out_until > datetime.now(timezone.utc)
        
        
        timeout_was_applied = before.timed_out_until != after.timed_out_until

        if is_currently_timed_out and timeout_was_applied:
            if player and isinstance(player, Player):
                try:
                    
                    player.queue.clear()
                    
                    if hasattr(player, "music_cache"):
                        await player.music_cache.clear_guild_cache(after.guild.id)
                        await player.music_cache.clear_loop_queue(after.guild.id)
                    
                    
                    if player.current:
                        await player.stop()
                        
                    
                    await player.disconnect()
                    
                except Exception as e:
                    print(f" Error during timeout cleanup: {e}")


async def setup(bot : commands.AutoShardedBot):
    await bot.add_cog(VoiceEvents(bot))