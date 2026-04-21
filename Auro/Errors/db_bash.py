import pomice
import asyncio
from databases.music_storage import MusicStorage


class TrackHealer:
    def __init__(self):

        self.storage = MusicStorage()

    async def repair(self, query: str) -> str:

        try:

            node = pomice.NodePool.get_node()
            if not node:
                print("🚨 Repair Error: No Pomice node available.")
                return None

            results: pomice.SearchResult = await node.get_tracks(
                query=f"ytmsearch:{query}"
            )

            if not results or not results.tracks:
                print(f"❌ Repair Failed: No results found for '{query}'")
                return None

            fresh_track = results.tracks[0]
            new_hash = fresh_track.track
            new_title = fresh_track.title

            await self.storage.save_to_storage(
                query=query,
                track_hash=new_hash,
                title=new_title,
                source="YouTube (Self-Healed)",
            )

            print(f"✅ Self-Healing Complete: {new_title}")
            return new_hash

        except Exception as e:
            print(f"🚨 Repair System Exception: {e}")
            return None


async def setup(bot):
    print("✅ db_bash extension acknowledged.")
