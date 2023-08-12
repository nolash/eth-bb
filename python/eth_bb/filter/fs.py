# standard imports
import os
import logging

# external imports
from hexathon import strip_0x

# local imports
from eth_bb.filter.mem import Filter as MemFilter

logg = logging.getLogger(__name__)


class Filter(MemFilter):

    def __init__(self):
        super(Filter, self).__init__()
        self.p = None


    def connect_store(self, ctx):
        self.p = ctx['usr'].get('bbpath')
        dp = os.path.join(self.p, '.resolve')
        os.makedirs(dp, exist_ok=True)
     

    def add(self, time, author, topic, hsh, ctx):
        dp = os.path.join(self.p, '.resolve')
        os.makedirs(dp, exist_ok=True)
        fp = os.path.join(dp, hsh)

        data = strip_0x(topic)
        data += strip_0x(author)
        data += time.strftime("%Y%m%d")
        f = open(fp, 'a')
        f.write(data)
        f.close()
        super(Filter, self).add(time, author, topic, hsh, ctx) 


    def store_item_for(self, author, topic, time, content, hsh):
        logg.debug('store item for {} {} {} {}'.format(time, author, topic, hsh))
        dp = os.path.join(self.p, author, topic)
        os.makedirs(dp, exist_ok=True)

        fp = os.path.join(dp, time)
        f = open(fp, 'a')
        f.write(content)
        f.write("\n")
        f.close()


    def store_item(self, content, hsh):
        fp = os.path.join(self.p, '.resolve', hsh)
        f = open(fp, 'r')
        i = 0
        csz = 64+40+8
        while True:
            r = f.read(csz)
            if r == '':
                break
            topic = r[:64]
            author = r[64:64+40]
            time = r[64+40:]
            self.store_item_for(author, topic, time, content, hsh)
        f.close()
        os.unlink(fp)
