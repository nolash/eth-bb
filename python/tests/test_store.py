# standard imports
import os
import unittest
import logging
import datetime
import tempfile
import shutil

# external imports
import faker 

# local imports
from eth_bb.store.ring import Store as RingStore

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestRingStore(unittest.TestCase):

    def setUp(self):
        self.d = tempfile.mkdtemp()


    def tearDown(self):
        shutil.rmtree(self.d)


    def test_ring_put_prepend(self):
        store = RingStore(self.d, 4096, reverse=True)
        topic = os.urandom(32)
        author = os.urandom(20)
        topic_hex = topic.hex()
        author_hex = author.hex()
        fg = faker.Faker()
        data = fg.texts(32)
        lp = 0
        for v in data:
            hsh = os.urandom(32)
            hsh_hex = hsh.hex()
            store.put(author_hex, topic_hex, hsh_hex, datetime.datetime.utcnow(), v)

            fp = os.path.join(self.d, author_hex, topic_hex, 'index.txt')
            f = open(fp, 'r')
            r = f.read()
            f.close()
            l = len(r)
            logg.debug('ll {}'.format(l))
            self.assertLessEqual(l, 4096)


    def test_ring_put_append(self):
        store = RingStore(self.d, 1024)
        topic = os.urandom(32)
        author = os.urandom(32)
        topic_hex = topic.hex()
        author_hex = author.hex()
        fg = faker.Faker()
        data = fg.texts(32)
        for v in data:
            hsh = os.urandom(32)
            hsh_hex = hsh.hex()
            store.put(author_hex, topic_hex, hsh_hex, datetime.datetime.utcnow(), v)

        fp = os.path.join(self.d, author_hex, topic_hex, 'index.txt')
        f = open(fp, 'r')
        r = f.read()
        f.close()
        self.assertLessEqual(len(r), 1024)
        logg.debug('r {}'.format(len(r)))


if __name__ == '__main__':
    unittest.main()
