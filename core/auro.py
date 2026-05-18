import asyncio
import datetime
import os
import discord
from discord.ext import commands
import pomice
from util.emojis import Emojis

# --- Lavalink Core Node Configuration ---
LAVALINK_HOST = "127.0.0.1"
LAVALINK_PORT = 2333
LAVALINK_PASSWORD = "youshallnotpass"
LAVALINK_SECURE = False
LAVALINK_IDENTIFIER = "Auro"


class Auro(commands.AutoShardedBot):

    def __init__(self):
        intents = discord.Intents.all()
        self.black_list = []
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

        await asyncio.sleep(5)

        
        feature_folders = [
            "Auro/Gen",
            "Auro/Music",
            "Auro/dev",
            "Auro/Errors",
            "Auro/Server",
            "Auro/Events",
            "Auro/Website",
            "Auro/status",
        ]

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

        
        async def pomice_setup():
            connected = False
            while not connected:
                try:
                    await pomice.NodePool.create_node(
                        identifier=LAVALINK_IDENTIFIER,
                        bot=self,
                        host=LAVALINK_HOST,
                        port=LAVALINK_PORT,
                        password=LAVALINK_PASSWORD,
                        secure=LAVALINK_SECURE,
                    )
                    print(
                        f"{self.get_time()} | INFO      | Pomice: Node connection initiated."
                    )
                    connected = True
                except Exception as e:
                    print(
                        f"{self.get_time()} | ERROR     | Pomice: Setup failed: {e}"
                    )
                    await asyncio.sleep(5)

        self.loop.create_task(pomice_setup())

    # --- Pomice Engine Framework Listeners ---

    @commands.Cog.listener()
    async def on_pomice_node_ready(self, node: pomice.Node):
        print(
            f"{self.get_time()} | SUCCESS   | Pomice: Node {node.identifier} is fully CONNECTED."
        )

    @commands.Cog.listener()
    async def on_pomice_node_disconnect(self, node: pomice.Node, reason: str, code: int):
        print(
            f"{self.get_time()} | WARNING   | Pomice: Node {node.identifier} disconnected! Reason: {reason} (Code: {code})"
        )        
        reconnected = False
        while not reconnected:
            await asyncio.sleep(5)
            try:
                print(
                    f"{self.get_time()} | INFO      | Pomice: Attempting to reconnect node {node.identifier}..."
                )

                await pomice.NodePool.create_node(
                    identifier=node.identifier,
                    bot=self,
                    host=node.host,
                    port=node.port,
                    password=node.password,
                    secure=node.secure,
                )
                print(
                    f"{self.get_time()} | SUCCESS   | Auro Engine [Node: {node.identifier}] is back online!"
                )
                reconnected = True
            except Exception as e:
                print(
                    f"{self.get_time()} | ERROR     | Pomice: Reconnection failed: {e}. Retrying in 5 seconds..."
                )

    # --- Gateway Infrastructure Listeners ---

    async def on_ready(self):
        print(
            f"{self.get_time()} | INFO      | Auro is Live | User: {self.user}"
        )
        print(
            f"{self.get_time()} | INFO      | Shard Topology: {self.shard_count} active shard(s)"
        )

    async def on_shard_ready(self, shard_id):
        print(f"{self.get_time()} | INFO      | Shard #{shard_id} is now ONLINE.")

    async def close(self):
        print(
            f"{self.get_time()} | INFO      | Auro Shutdown: Closing active connections..."
        )
        try:
            await pomice.NodePool.disconnect()
            print(f"{self.get_time()} | SUCCESS   | Pomice: All node sessions closed.")
        except Exception as e:
            print(f"{self.get_time()} | ERROR     | Pomice teardown failed: {e}")

        await super().close()