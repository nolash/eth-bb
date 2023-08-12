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
logg = logging.getLogger()


class TestFsindex(unittest.TestCase):

    def setUp(self):
        self.dp = tempfile.mkdtemp()
        self.idx = FsIndex(self.dp)


    def tearDown(self):
        shutil.rmtree(self.dp)


    def test_(self):
        topic = b'\xee' * 32
        author = b'\xdd' * 20
        topic_hex = topic.hex()
        author_hex = author.hex()
        self.idx.load_cursor(author_hex, topic_hex)
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

    
    def test_list(self):
        topic_one = b'\xee' * 32
        topic_two = b'\xaa' * 32
        alice = b'\xdd' * 20
        bob = b'\xcc' * 20
        hsh = os.urandom(32)
        topic_one_hex = topic_one.hex()
        topic_two_hex = topic_two.hex()
        alice_hex = alice.hex()
        bob_hex = bob.hex()

        time = datetime.datetime.utcnow()
        timestamp = datetime.datetime.timestamp(time)
        time = datetime.datetime.fromtimestamp(int(timestamp))

        idxb = FsIndex(self.dp, namespace='foo')
        idxb.put(alice_hex, topic_one_hex, hsh.hex(), time)
        idxb.put(bob_hex, topic_one_hex, hsh.hex(), time)
        idxb.put(bob_hex, topic_two_hex, hsh.hex(), time)

        ra = idxb.authors()
        self.assertEqual(len(ra), 2)

        r = idxb.topics(alice_hex)
        self.assertEqual(len(r), 1)
    
        r = idxb.topics(bob_hex)
        self.assertEqual(len(r), 2)


    def test_iter(self):
        topic_one = b'\xee' * 32
        topic_two = b'\xaa' * 32
        alice = b'\xdd' * 20
        bob = b'\xcc' * 20
        hsh = os.urandom(32)
        topic_one_hex = topic_one.hex()
        topic_two_hex = topic_two.hex()
        alice_hex = alice.hex()
        bob_hex = bob.hex()

        time = datetime.datetime.utcnow()
        timestamp = datetime.datetime.timestamp(time)
        time = datetime.datetime.fromtimestamp(int(timestamp))

        idxb = FsIndex(self.dp, namespace='foo')
        idxb.put(alice_hex, topic_one_hex, hsh.hex(), time)
        idxb.put(bob_hex, topic_one_hex, hsh.hex(), time)
        idxb.put(bob_hex, topic_two_hex, hsh.hex(), time)

        r = []
        for v in iter(idxb):
            vv = v[0] + v[1]
            logg.debug('adding {}'.format(vv))
            r.append(vv)
        self.assertEqual(len(r), 3)
        self.assertListEqual(r, [
            bob_hex + topic_two_hex,
            bob_hex + topic_one_hex,
            alice_hex + topic_one_hex,
            ])


if __name__ == '__main__':
    unittest.main()
