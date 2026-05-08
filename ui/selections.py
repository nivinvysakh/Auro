import discord
import re
from typing import List
from util.emojis import Emojis
import pomice

class TrackSelectionView(discord.ui.View):
    def __init__(self, tracks: List[pomice.Track]):
        super().__init__(timeout=30)
        self.selected_track = None
        
        options = []
        for i, track in enumerate(tracks):
            clean_name = re.sub(r'\(Official.*?\)|\[Official.*?\]|Official Video|Music Video|4K|HQ|HD|Full HD', '',track.title, flags=re.IGNORECASE)
            clean_name = " ".join(clean_name.split()).strip()
            if len(clean_name) > 97 :
                display_label = f"{clean_name[:97]}..."
            else :
                display_label = clean_name or track.title[:100]
            options.append(discord.SelectOption(
                label=display_label,
                description=f"By {track.author} | {track.length // 60000}m",
                value=str(i),
                emoji=Emojis.star_animate
            ))

        self.select = discord.ui.Select(placeholder="Choose the version...", options=options)
        self.select.callback = self.callback
        self.add_item(self.select)
        self.tracks = tracks

    async def callback(self, interaction: discord.Interaction):
        self.selected_track = self.tracks[int(self.select.values[0])]
        self.stop()
        await interaction.response.send_message(f"{Emojis.success} Selected: **{self.selected_track.title}**", ephemeral=True)