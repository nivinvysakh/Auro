import re
from typing import Tuple

def split_track_title(title: str) -> Tuple[str, str]:

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