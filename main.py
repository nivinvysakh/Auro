import asyncio
import os
import colorama
from dotenv import load_dotenv
from core.auro import Auro
from databases import init_dbs
from colorama import Style ,Fore
load_dotenv()
colorama.init(autoreset=True)
AURO_BANNER = r"""
    ___       __  ______  ____ 
   /   |     / / / / __ \/ __ \
  / /| |    / / / / /_/ / / / /
 / ___ |   / /_/ / _, _/ /_/ / 
/_/  |_|   \____/_/ |_|\____/  
      - The Music Engine -
"""
async def run_auro():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.LIGHTBLUE_EX}{AURO_BANNER}")
    print(f"{Fore.LIGHTBLUE_EX}{'='*40}")
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