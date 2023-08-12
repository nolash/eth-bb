# standard imports
import os
import logging
import datetime

# external imports
from hexathon import strip_0x

# local imports
from eth_bb.filter.mem import Filter as MemFilter

logg = logging.getLogger(__name__)


class Filter(MemFilter):

    def __init__(self):
        super(Filter, self).__init__()
        self.p = None


    def prepare(self, ctx):
        super(Filter, self).prepare(ctx)
        idx = ctx['usr'].get('bbindex')
        if idx == 'fs':
            self.resolve_index_push = self.resolve_index_push_fs
            self.resolve_index_process = self.resolve_index_process_fs


    def connect_store(self, ctx):
        self.p = ctx['usr'].get('bbpath')
        dp = os.path.join(self.p, '.resolve')
        os.makedirs(dp, exist_ok=True)
    

    def resolve_index_push_fs(self, time, author, topic, hsh):
        logg.debug('push fs')
        dp = os.path.join(self.p, '.resolve')
        os.makedirs(dp, exist_ok=True)
        fp = os.path.join(dp, hsh)

        data = strip_0x(topic)
        data += strip_0x(author)
        data += time.strftime("%Y%m%d%H%M%S")
        f = open(fp, 'a')
        f.write(data)
        f.close()


    def resolve_index_process_fs(self, content, hsh):
        fp = os.path.join(self.p, '.resolve', hsh)
        f = open(fp, 'r')
        i = 0
        while True:
            r = f.read(self.index_size)
            if r == '':
                break
            topic = r[:64]
            author = r[64:64+40]
            time = r[64+40:]
            self.store_item_for(time, author, topic, content, hsh)
        f.close()
        os.unlink(fp)


    def format(self, time, author, topic, content, hsh):
        return '[{}]\n\n{}\n---\n\n'.format(time, content)


    def store_item_for(self, time, author, topic, content, hsh):
        date = time[:8]
        time = datetime.datetime.strptime(time, "%Y%m%d%H%M%S")
        logg.debug('store item for {} {} {} {}'.format(time, author, topic, hsh))
        dp = os.path.join(self.p, author, topic)
        os.makedirs(dp, exist_ok=True)

        data = self.format(time, author, topic, content, hsh)
        fp = os.path.join(dp, date)
        f = open(fp, 'a')
        f.write(data)
        f.close()


    def store_item(self, content, hsh):
        self.resolve_index_process(content, hsh)
