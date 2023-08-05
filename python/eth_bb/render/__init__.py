# standard imports
import enum
import sys

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


class Renderer:

    def __init__(self, w=sys.stdout, verify=False):
        self.w = w
        self.verify = verify


    # add one unit of content to the renderer.
    # may be subject to verification
    def write(self, v):
        raise NotImplementedError('override this method')


    # output ALL content to the writer
    def flush(self, w=None):
        raise NotImplementedError('override this method')
