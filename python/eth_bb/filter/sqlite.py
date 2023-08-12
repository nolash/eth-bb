# standard imports
import os
import logging
import sqlite3

# local imports
from eth_bb.filter.base import Filter as BaseFilter

logg = logging.getLogger(__name__)


class Filter(BaseFilter):

    def connect_store(self, ctx):
        dp = ctx['usr'].get('bbpath')
        if self.store_spec != None:
            return

        if dp == None:
            dp = '.'
        fp = os.path.join(dp, 'ethbb.sql')
        self.store_spec = fp

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


    def resolve_history(self):
        store = sqlite3.connect(self.store_spec)
        cur = store.cursor()
        sql = 'SELECT hash from posts where resolved = 0';
        res = cur.execute(sql)
        for v in res.fetchall():
            r = self.resolve_item(v[0])
            #self.store_item(r, v[0])


    def store_item(self, content, hsh):
        store = sqlite3.connect(self.store_spec)
        cur = store.cursor()
        sql = 'UPDATE posts SET content = "{}", resolved = 1 WHERE hash = "{}" AND resolved = 0'.format(content, hsh)
        logg.info('update {}'.format(sql))
        cur.execute(sql)
        store.commit()


    def resolve_index_push(self, time, author, topic, hsh):
        pass


    def resolve_index_process(self, content, hsh):
        pass


    def add(self, time, author, topic, hsh, ctx):
        store = sqlite3.connect(self.store_spec)
        cur = store.cursor()
        sql = "INSERT INTO posts (date, address, context, hash) VALUES ('{}','{}','{}','{}')".format(time, author, topic, hsh)
        cur.execute(sql)
        store.commit()
        self.resolve(time, author, topic, hsh)
        logg.info('added author entry {} ctx {} time {}'.format(author, topic, time))
