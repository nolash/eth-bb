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
        self.resolver_history_thread = threading.Thread(target=self.resolve_history)
        self.resolver_spec = None
        self.resolver = None
        self.q = queue.Queue()


    def prepare(self, ctx=None):
        if ctx != None:
            self.connect_resolver(ctx['usr'].get('bbresolver'))
            self.connect_store(ctx['usr'].get('bbpath'))
            self.connect()


    def stop(self):
        if self.resolver == None:
            return
        logg.info('collecting ethbb resolver threads')
        self.resolver_history_thread.join()
        self.q.put_nowait(None)
        self.q.join()
        self.resolver_thread.join()


    def resolve_history(self):
        pass


    def resolve_item(self, v):
        r = self.resolver.resolve(self.resolver_spec, v)
        if len(r) == 0:
            logg.warning('resolve hash {} failed'.format(v))
            return
        self.store_item(r, v)


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


    def connect(self):
        if self.resolver:
            self.resolver_history_thread.start()
            self.resolver_thread.start()


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
        author = strip_0x(tx.inputs[0])
        context = strip_0x(data[8:64+8])
        content = strip_0x(data[8+64:])
        self.add(time, author, context, content)


    def connect_store(self, dp):
        pass


    def store_item(self, content, hsh):
        print('store {} {}'.format(content, hsh))


    def add(self, time, author, ctx, content):
        logg.debug('adding {} {}'.format(time, author))
        if self.resolver:
            self.q.put_nowait(content)
