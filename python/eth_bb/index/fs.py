# standard imports
import os
import logging
import datetime

# external imports
from hexathon import strip_0x

# local imports
from .base import Index

logg = logging.getLogger(__name__)


class FsIndex(Index):

    def __init__(self, path, namespace='bb'):
        super(FsIndex, self).__init__()
        self.step = 32+4
        self.path = os.path.join(path, '.index')
        self.ns = namespace
        os.makedirs(self.path, exist_ok=True)
        self.load_cursor()
        

    def load_cursor(self):
        cp = os.path.join(self.path, '.' + self.ns)
        try:
            f = open(cp, 'rb')
            r = f.read(4)
            f.close()
            self.crsr = int.from_bytes(r, byteorder='big')
            logg.debug('cursor "{}" is {}'.format(self.ns, self.crsr))
        except FileNotFoundError:
            self.save_cursor(0) 
   

    def save_cursor(self, v):
        cp = os.path.join(self.path, '.' + self.ns)
        d = v.to_bytes(4, byteorder='big')
        f = open(cp, 'wb')
        r = f.write(d)
        f.close()
        self.crsr = v
        logg.debug('cursor "{}" saved as {}'.format(self.ns, v))


    def put(self, author, topic, hsh, time):
        (author, topic, hsh, time,) = self.clean(author, topic, hsh, time)
        timestamp = int(time.timestamp())
        b = bytes.fromhex(hsh)
        b += timestamp.to_bytes(4, byteorder='big')
        dp = os.path.join(self.path, author)
        os.makedirs(dp, exist_ok=True)
        fp = os.path.join(dp, topic)
        f = open(fp, 'ab')
        f.write(b)
        f.close()
        logg.debug('put to {}'.format(fp))
        return (time, author, topic, hsh,)


    def next(self, author, topic):
        (author, topic, hsh_void, time_void) = self.clean(author, topic)
        fp = os.path.join(self.path, author, topic)
        logg.debug('lokking fp {}'.format(fp))
        try:
            f = open(fp, 'rb')
        except FileNotFoundError:
            return None
        f.seek(self.crsr)
        r = f.read(self.step)
        if len(r) == 0:
            f.close()
            return None
        self.save_cursor(f.tell())
        f.close()
        hsh = r[:32]
        timestamp = int.from_bytes(r[32:], byteorder='big')
        time = datetime.datetime.fromtimestamp(timestamp)
        return (hsh.hex(), time,)