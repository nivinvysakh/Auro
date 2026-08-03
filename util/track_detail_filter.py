import re
from typing import Tuple

def split_track_title(title: str) -> Tuple[str, str]:
    """
    A function that splits a track title into the main title and any extra details (like featuring artists, remix info, etc.). It uses regex to identify common patterns in track titles and separates them accordingly. If no patterns are found, it returns the original title and an empty string for extra details. If the title is longer than 40 characters, it will split at the last space before the 40th character.
    """

    if not title:
        return "Unknown Track", ""


    pattern = r"^(.*?)\s*([([◄]?\s*(?:feat\.?|ft\.?|remix|mix|prod\.)|[\(\[][^)]*[-_•].*|[([◄])"
    match = re.match(pattern, title, re.IGNORECASE)

    if match:
        main_title = match.group(1).strip()
        
        extra_details = title[len(main_title):].strip()
        return main_title, extra_details

   
    if len(title) > 40:
        
        cut_index = title.rfind(" ", 0, 40)
        if cut_index == -1:
            cut_index = 40
        return title[:cut_index].strip(), title[cut_index:].strip()

    return title, ""