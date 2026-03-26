from .noprefix import NoprefixDatabase
from .Bot_Prefix import PrefixDatabase
from .badges import BadgesDatabase



noprefix = NoprefixDatabase()
prefix = PrefixDatabase()
badges = BadgesDatabase()
init_db_list = [
    ("noprefixDB", noprefix),
    ("prefixDB", prefix),
    ("badgesDB", badges),
]

async def init_dbs():
    for name, db in init_db_list:
        try:
            await db.init_db()
            print(f"{name} initialized successfully.")
        except Exception as e:
            print(f"An error occurred while initializing {name}: {e}")
