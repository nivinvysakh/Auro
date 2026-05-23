import re

def clean_track_title(title: str, max_chars: int = 40) -> str:
    if not title:
        return "Unknown Track"

    junk_patterns = [
        r'\s*[\[\(](official|music|video|audio|lyric|hd|4k|hq)[\]\)]\s*',
        r'\s*[\[\(]video\s*clip[\]\)]\s*',
        r'\s*\|\s*official\s*(music\s*)?(video|audio)\s*',
        r'\s*-\s*official\s*(music\s*)?(video|audio)\s*',
        r'\s*[\[\(](f|feat|featuring|ft)\.?\s+[^\]\)]+[\]\)]\s*',
        r'\s*[\[\(][^\]\)]*(remix|mix|edit|version)[\]\)]\s*',
        r'\s*~\s*.*',
    ]
    
    cleaned = title
    for pattern in junk_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
    cleaned = re.sub(re.compile(r'\s+'), ' ', cleaned)
    cleaned = cleaned.strip().strip('-').strip('|').strip()

    if len(cleaned) > max_chars:
        return cleaned[:max_chars - 3].strip() + "..."
        
    return cleaned if cleaned else title