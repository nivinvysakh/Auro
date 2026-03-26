import discord
from discord.ext import commands
import os
import datetime
import sys

class Auro(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="a!",
            intents=intents,
            help_command=None,
            chunk_guilds_at_startup=False,
            case_insensitive=True
        )

    def get_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    async def setup_hook(self):
        print(f"{self.get_time()} | INFO     | Auro Infrastructure: Initializing Shards...")
    
        
        feature_folders = ['Auro/Gen', 'Auro/Music', 'Auro/dev']
        
        for folder in feature_folders:
           
            if not os.path.isdir(folder):
                continue

            for filename in os.listdir(folder):
                
                if filename.endswith(".py") and not filename.startswith("__"):
                    cog_path = f"{folder}.{filename[:-3]}"
                    try:
                        await self.load_extension(f"Auro.{folder.split('/')[-1]}.{filename[:-3]}")
                        print(f"{self.get_time()} | SUCCESS  | Module Loaded: {cog_path}")
                    except Exception as e:
                        print(f"{self.get_time()} | ERROR    | Failed to load {cog_path}: {e}")

        await self.tree.sync()
        print(f"{self.get_time()} | SUCCESS  | Auro Slash Commands: Synced.")

    async def on_ready(self):
        print(f"{self.get_time()} | INFO     | Auro is Live | User: {self.user}")
        print(f"{self.get_time()} | INFO     | Shard Topology: {self.shard_count} active shard(s)")

    async def on_shard_ready(self, shard_id):
        print(f"{self.get_time()} | INFO     | Shard #{shard_id} is now ONLINE.")