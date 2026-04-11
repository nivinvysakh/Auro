import discord
from discord.ext import commands
import os
import datetime
import pomice
import asyncio


class Auro(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="a!",
            intents=intents,
            help_command=None,
            chunk_guilds_at_startup=False,
            case_insensitive=True,
        )

    def get_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    async def setup_hook(self):
        print(
            f"{self.get_time()} | INFO      | Auro Infrastructure: Initializing Shards..."
        )

        async def pomice_setup():
            try:
                await pomice.NodePool.create_node(
                    identifier="Auro",
                    bot=self,
                    host="127.0.0.1",
                    port=2333,
                    password="youshallnotpass",
                    secure=False,
                )
                print(
                    f"{self.get_time()} | INFO      | Pomice: Node connection initiated."
                )
            except Exception as e:
                print(f"{self.get_time()} | ERROR     | Pomice: Setup failed: {e}")

        self.loop.create_task(pomice_setup())

        feature_folders = ["Auro/Gen", "Auro/Music", "Auro/dev", "Auro/Errors"]

        for folder in feature_folders:
            if not os.path.isdir(folder):
                continue

            for filename in os.listdir(folder):
                if filename.endswith(".py") and not filename.startswith("__"):

                    cog_name = filename[:-3]
                    folder_name = folder.split("/")[-1]
                    try:
                        await self.load_extension(f"Auro.{folder_name}.{cog_name}")
                        print(
                            f"{self.get_time()} | SUCCESS   | Module Loaded: {folder_name}.{cog_name}"
                        )
                    except Exception as e:
                        print(
                            f"{self.get_time()} | ERROR     | Failed to load {cog_name}: {e}"
                        )

        await self.tree.sync()
        print(f"{self.get_time()} | SUCCESS   | Auro Slash Commands: Synced.")

    @commands.Cog.listener()
    async def on_pomice_node_ready(self, node: pomice.Node):
        print(
            f"{self.get_time()} | SUCCESS   | Pomice: Node {node.identifier} is fully CONNECTED."
        )

    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.custom, name="Auro", state="🍃"
            ),
        )
        print(f"{self.get_time()} | INFO      | Auro is Live | User: {self.user}")
        print(
            f"{self.get_time()} | INFO      | Shard Topology: {self.shard_count} active shard(s)"
        )

    async def on_shard_ready(self, shard_id):
        print(f"{self.get_time()} | INFO      | Shard #{shard_id} is now ONLINE.")
