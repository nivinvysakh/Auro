from .badges import BadgesDatabase
from .music_cache import MusicCache
from .music_storage import MusicStorage

badges = BadgesDatabase()
music_cache = MusicCache()
music_storage = MusicStorage()
init_db_list = [
    ("badgesDB", badges),
    ("musicCacheDB",music_cache),
    ("Music_Bash_System",music_storage)
]   


async def init_dbs():
    for name, db in init_db_list:
        try:
            await db.init_db()
            print(f"{name} initialized successfully.")
        except Exception as e:
            print(f"An error occurred while initializing {name}: {e}")
