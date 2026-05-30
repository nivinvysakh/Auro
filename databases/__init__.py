from .badges import BadgesDatabase
from .music_cache import MusicCache
from .music_storage import MusicStorage
from .prefix import SettingsStorage
from .tracking import TrackingStorage
badges = BadgesDatabase()
music_cache = MusicCache()
music_storage = MusicStorage()
prefix = SettingsStorage()
tracking = TrackingStorage()
init_db_list = [
    ("PrefixDb", prefix),
    ("badgesDb", badges),
    ("SessionsDb" , tracking),
    ("musicCacheDB", music_cache),
    ("Music_Bash_System", music_storage),
]


async def init_dbs():
    for name, db in init_db_list:
        try:
            await db.init_db()
            print(f"{name} initialized successfully.")
        except Exception as e:
            print(f"An error occurred while initializing {name}: {e}")
