# standard imports
import os
import logging
import datetime

# external imports
from hexathon import strip_0x
from hexathon import valid as hex_valid
from hexathon import uniform

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
        

    def load_cursor(self, author, topic):
        crsr = 0
        cp = os.path.join(self.path, author, '.' + self.ns + '_' + topic)
        try:
            f = open(cp, 'rb')
            r = f.read(4)
            f.close()
            crsr = int.from_bytes(r, byteorder='big')
            logg.debug('cursor "{}" for {}/{} load {}'.format(self.ns, author, topic, crsr))
        except FileNotFoundError:
            self.save_cursor(author, topic, 0) 
        return crsr
   

    def save_cursor(self, author, topic, v):
        dp = os.path.join(self.path, author)
        os.makedirs(dp, exist_ok=True)
        cp = os.path.join(dp, '.' + self.ns + '_' + topic)
        d = v.to_bytes(4, byteorder='big')
        f = open(cp, 'wb')
        r = f.write(d)
        f.close()
        logg.debug('cursor "{}" for {}/{} save {}'.format(self.ns, author, topic, v))
        return v


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
        return (time, author, topic, hsh,)


    def next(self, author, topic):
        (author, topic, hsh_void, time_void) = self.clean(author, topic)
        fp = os.path.join(self.path, author, topic)
        logg.debug('lokking fp {}'.format(fp))
        try:
            f = open(fp, 'rb')
        except FileNotFoundError:
            return None
        crsr = self.load_cursor(author, topic)
        f.seek(crsr)
        r = f.read(self.step)
        if len(r) == 0:
            f.close()
            return None
        self.save_cursor(author, topic, f.tell())
        f.close()
        hsh = r[:32]
        timestamp = int.from_bytes(r[32:], byteorder='big')
        time = datetime.datetime.fromtimestamp(timestamp)
        return (hsh.hex(), time,)


    def authors(self):
        return self.__list(self.path)
        

    def topics(self, author):
        path = os.path.join(self.path, author)
        return self.__list(path)
       

    def __list(self, path):
        r = []
        o = None
        try:
            o = os.listdir(path)
        except FileNotFoundError:
            return r
        for v in o:
            if v[0] == '.':
                continue
            if not hex_valid(v):
                logg.warning('invalid entry {} in index'.format(v))
                continue
            r.append(uniform(v))
        return r
