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
        self.resolver_thread = threading.Thread(target=self.resolve)
        self.resolver_spec = None
        self.resolver = None
        self.q = queue.Queue()


    def stop(self):
        logg.info('collecting ethbb resolver thread')
        self.q.put_nowait(None)
        self.q.join()
        self.resolver_thread.join()


    def resolve_item(self, v):
        r = self.resolver.resolve(self.resolver_spec, v)
        if len(r) == 0:
            logg.warning('resolve hash {} failed'.format(v))
            return
        store = sqlite3.connect(self.store_spec)
        cur = store.cursor()
        sql = 'UPDATE posts SET content = "{}", resolved = 1 WHERE hash = "{}" AND resolved = 0'.format(r, v)
        logg.info('update {}'.format(sql))
        cur.execute(sql)
        store.commit()


    def resolve(self):
        while True:
            try:
                r = self.q.get(timeout=1)
            except queue.Empty:
                continue
            if r == None:
                break
            self.resolve_item(r)
            self.q.task_done()
        self.q.task_done()


    def connect_resolver(self, resolver_spec):
        if resolver_spec == None:
            return
        m = module_for(resolver_spec)
        if m != None:
            self.resolver_spec = resolver_spec
            self.resolver = m


    def connect_store(self, dp):
        if self.store_spec != None:
            return

        if dp == None:
            dp = '.'
        fp = os.path.join(dp, 'ethbb.sql')
        self.store_spec = fp

        if self.resolver:
            self.resolver_thread.start()

        store = sqlite3.connect(self.store_spec)
        cur = store.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS posts (
id INTEGER PRIMARY_KEY AUTO_INCREMENT,
date DATETIME,
address CHAR(40) NOT NULL,
context CHAR(64) NOT NULL,
hash CHAR(64) NOT NULL,
content TEXT,
resolved INT NOT NULL default 0
)
""")
        store.commit()


    def add(self, time, author, ctx, content):
        store = sqlite3.connect(self.store_spec)
        cur = store.cursor()
        sql = "INSERT INTO posts (date, address, context, hash) VALUES ('{}','{}','{}','{}')".format(time, author, ctx, content)
        cur.execute(sql)
        store.commit()
        if self.resolver:
            self.q.put_nowait(content)
        logg.info('added author entry {} ctx {} time {}'.format(author, ctx, time))


    def filter(self, conn, block, tx, **kwargs):
        ctx = kwargs.get('ctx')
        self.connect_resolver(ctx['usr'].get('bbresolver'))
        self.connect_store(ctx['usr'].get('bbpath'))
        if tx.status != Status.SUCCESS:
            return False
        if len(tx.payload) < 8+64+64:
            return False
        data = strip_0x(tx.payload)
        if data[:8] != 'd1de592a':
            return False

        logg.info('ok data {}'.format(data))
        time = datetime.datetime.fromtimestamp(block.timestamp)
        author = strip_0x(tx.inputs[0])
        context = strip_0x(data[8:64+8])
        content = strip_0x(data[8+64:])
        self.add(time, author, context, content)
