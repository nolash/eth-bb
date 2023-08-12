# standard imports
import unittest
import tempfile
import shutil
import logging
import datetime
import os

# local imports
from eth_bb.index.fs import FsIndex

logging.basicConfig(level=logging.DEBUG)


class TestFsindex(unittest.TestCase):

    def setUp(self):
        self.dp = tempfile.mkdtemp()
        self.idx = FsIndex(self.dp)


    def tearDown(self):
        shutil.rmtree(self.dp)


    def test_(self):
        self.idx.load_cursor()
        topic = b'\xee' * 32
        author = b'\xdd' * 20
        hsh = b'\xcc' * 32
        time = datetime.datetime.utcnow()
        timestamp = datetime.datetime.timestamp(time)
        time = datetime.datetime.fromtimestamp(int(timestamp))
        self.idx.put(author.hex(), topic.hex(), hsh.hex(), time)
        r = self.idx.next(author.hex(), topic.hex())
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], hsh.hex())
        self.assertEqual(r[1], time)

        r = self.idx.next(author.hex(), topic.hex())
        self.assertEqual(r, None)


    def test_race(self):
        topic = b'\xee' * 32
        author = b'\xdd' * 20
        topic_hex = topic.hex()
        author_hex = author.hex()

        for i in range(3):
            b = os.urandom(36)
            hsh = b[:32]
            time = datetime.datetime.fromtimestamp(int.from_bytes(b[32:], byteorder='big'))
            self.idx.put(author_hex, topic_hex, hsh.hex(), time)

        idxb = FsIndex(self.dp, namespace='foo')
        idxb.put(author_hex, topic_hex, hsh.hex(), time)
        b = os.urandom(36)
        hsh = b[:32]
        time = datetime.datetime.fromtimestamp(int.from_bytes(b[32:], byteorder='big'))

        a = []
        b = []
        for i in range(4):
            r = self.idx.next(author_hex, topic_hex)
            self.assertIsNotNone(r)
            a.append(r)
            r = idxb.next(author_hex, topic_hex)
            self.assertIsNotNone(r)
            b.append(r)
        self.assertListEqual(a, b)
   

if __name__ == '__main__':
    unittest.main()
