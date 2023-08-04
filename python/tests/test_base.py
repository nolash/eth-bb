# standard imports
import os
import unittest
import json
import logging

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.constant import ZERO_CONTENT
from chainlib.connection import RPCConnection
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from hexathon import strip_0x
from hexathon import same as same_hex

# local imports
from eth_bb import BB

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


hash_of_foo = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
hash_of_bar = 'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9'
hash_of_baz = 'baa5a0964d3320fbc0c6a922140453c8513ea24ab8fd0577034804a967248096'


class Test(EthTesterCase):

    def setUp(self):
        super(Test, self).setUp()
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BB(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.constructor(self.accounts[0])
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        self.conn.do(o)
        o = receipt(tx_hash)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
        self.address = to_checksum_address(r['contract_address'])
        logg.debug('smart contract published with hash {}'.format(tx_hash))


    def test_hash(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BB(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.add(self.address, self.accounts[0], hash_of_foo, hash_of_bar)
        self.conn.do(o)
        o = receipt(tx_hash)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash, o) = c.add(self.address, self.accounts[0], hash_of_foo, hash_of_baz)
        self.conn.do(o)
        o = receipt(tx_hash)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash, o) = c.add(self.address, self.accounts[0], hash_of_bar, hash_of_foo)
        self.conn.do(o)
        o = receipt(tx_hash)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.entry_count(self.address, self.accounts[0], hash_of_foo, sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 2)

        o = c.entry_count(self.address, self.accounts[0], hash_of_bar, sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 1)

        o = c.entry(self.address, self.accounts[0], hash_of_foo, 1, sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertTrue(same_hex(r, hash_of_baz))


if __name__ == '__main__':
    unittest.main()

