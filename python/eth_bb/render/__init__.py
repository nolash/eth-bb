# standard imports
import enum

class RenderMode(enum.Enum):
    
    RSS = 'application/rss+xml'


def mode_for(v):
    if v == 'application/rss+xml':
        return RenderMode.RSS
    return None


def mode_to_mime(mode):
    mode = mode.upper()
    a = getattr(RenderMode, mode)
    return a.value
