import discord
from typing import List
from util.emojis import Emojis
import pomice

class TrackSelectionView(discord.ui.View):
    def __init__(self, tracks: List[pomice.Track]):
        super().__init__(timeout=30)
        self.selected_track = None
        
        options = []
        for i, track in enumerate(tracks):
            options.append(discord.SelectOption(
                label=track.title[:100],
                description=f"By {track.author} | {track.length // 60000}m",
                value=str(i),
                emoji=Emojis.musicplaying
            ))

        self.select = discord.ui.Select(placeholder="Choose the version...", options=options)
        self.select.callback = self.callback
        self.add_item(self.select)
        self.tracks = tracks

    async def callback(self, interaction: discord.Interaction):
        self.selected_track = self.tracks[int(self.select.values[0])]
        self.stop()
        await interaction.response.send_message(f"✅ Selected: **{self.selected_track.title}**", ephemeral=True)