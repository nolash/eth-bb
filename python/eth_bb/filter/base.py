# standard imports
import logging
import sqlite3
import os
import datetime
import threading
import queue

# external imports
from hexathon import strip_0x
from chainsyncer.filter import SyncFilter
from chainlib.status import Status

# local imports
from eth_bb.resolve import module_for

logg = logging.getLogger(__name__)


class Filter(SyncFilter):

    def __init__(self):
        self.store_spec = None
        self.resolver_thread = threading.Thread(target=self.resolve_loop)
        self.resolver_history_thread = threading.Thread(target=self.resolve_history)
        self.resolver_spec = None
        self.resolver = None
        self.idx = None
        self.q = queue.Queue()


    def prepare(self, ctx=None):
        if ctx == None:
            return
        self.connect_index(ctx)
        self.connect_resolver(ctx)
        self.connect_store(ctx)
        self.start(ctx)


    def connect_index(self, ctx):
        idx_type = ctx['usr'].get('bbindex', None)
        if idx_type == 'fs':
            from eth_bb.index.fs import FsIndex
            path = ctx['usr'].get('bbpath', '.')
            self.idx = FsIndex(path)


    def stop(self):
        logg.info('collecting ethbb resolver threads')
        self.resolver_history_thread.join()
        self.q.put_nowait(None)
        self.q.join()
        self.resolver_thread.join()


    def resolve_history(self):
        if self.idx == None:
            return
        for v in iter(self.idx):
            logg.debug('history item {}'.format(v))
            self.q.put_nowait((v[0], v[1],))


    def resolve_item(self, author, topic, hsh, time):
        if self.resolver == None:
            return 
        r = self.resolver.resolve(self.resolver_spec, hsh)
        if len(r) == 0:
            logg.warning('resolve hash {} failed'.format(hsh))
            return
        self.store_item(author, topic, hsh, time, r)


    def resolve_loop(self):
        while True:
            try:
                r = self.q.get(timeout=1)
            except queue.Empty:
                continue
            if r == None:
                self.q.task_done()
                logg.info('exiting resolver loop')
                return
            author = r[0]
            topic = r[1]
            self.process_index(author, topic)
            self.q.task_done()


    def process_index(self, author, topic):
        if self.idx == None:
            return
        if self.resolver == None:
            return
        while True:
            r = self.idx.next(author, topic)
            if r == None:
                return
            self.resolve_item(author, topic, r[0], r[1])


    def connect_resolver(self, ctx):
        ctx_usr = ctx.get('usr')
        if ctx_usr == None:
            return
        resolver_spec = ctx_usr.get('bbresolver')
        if resolver_spec == None:
            return
        m = module_for(resolver_spec)
        if m != None:
            self.resolver_spec = resolver_spec
            self.resolver = m


    def start(self, ctx):
        self.resolver_history_thread.start()
        self.resolver_thread.start()


    def connect_store(self, ctx):
        ctx_usr = ctx.get('usr')
        if ctx_usr == None:
            return
        store_type = ctx_usr.get('bbstore')
        if store_type == 'fs':
            from eth_bb.store.date import FsDateStore
            dp = ctx_usr.get('bbpath', '.')
            dp = os.path.join(dp, '.content')
            self.store = FsDateStore(dp)
            logg.debug('have store {}'.format(self.store))


    def filter(self, conn, block, tx, **kwargs):
        ctx = kwargs.get('ctx')
        if tx.status != Status.SUCCESS:
            return False
        if len(tx.payload) < 8+64+64:
            return False
        data = strip_0x(tx.payload)
        if data[:8] != 'd1de592a':
            return False

        time = datetime.datetime.fromtimestamp(block.timestamp)
        author = strip_0x(tx.outputs[0])
        topic = strip_0x(data[8:64+8])
        content = strip_0x(data[8+64:])
        self.add(time, author, topic, content, ctx)
        return False


    def store_item(self, author, topic, hsh, time, content):
        if self.store != None:
            return self.store.put(author, topic, hsh, time, content)
        logg.debug('nostore for {} {} {} {}'.format(author, topic, hsh, time))


    def add(self, time, author, topic, hsh, ctx=None):
        if self.idx != None:
            self.idx.put(author, topic, hsh, time)
        self.resolve(time, author, topic, hsh)


    def resolve(self, time, author, topic, hsh):
        self.q.put_nowait((author, topic,))
