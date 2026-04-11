import asyncio
import os
from dotenv import load_dotenv
from core.auro import Auro
from databases import init_dbs

load_dotenv()


async def run_auro():
    try:
        await init_dbs()
        print("INFO     | All databases initialized successfully.")
        print()
    except Exception as e:
        print(f"ERROR    | Database Initialization Failure: {e}")
        return

    bot = Auro()

    async with bot:
        try:
            token = os.getenv("TOKEN")
            if not token:
                print("ERROR    | TOKEN not found in .env file.")
                return

            await bot.start(token)

        except Exception as e:
            print(f"ERROR    | Fatal Startup Failure: {e}")


if __name__ == "__main__":
    try:

        asyncio.run(run_auro())
    except KeyboardInterrupt:
        print("INFO     | Auro Shutdown: Process terminated by user.")
