# standard imports
import sys

class Builder():
    
    def __init__(self, *args, **kwargs):
        self.c = 0


    def write(self, v):
        sys.stdout.write('{}: {}'.format(self.c, v))
        self.c += 1


    def flush(self, w=None):
        pass
