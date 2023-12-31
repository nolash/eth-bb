# standard imports
import unittest
import json
import logging
import shutil
import tempfile
import datetime
import os

# external imports
from chainlib.eth.tx import Tx
from chainlib.eth.block import Block
from chainlib.eth.unittest.ethtester import EthTesterCase
from hexathon import strip_0x

# local imports
from eth_bb.unittest.filter import Filter
from eth_bb.filter.base import Filter as BaseFilter
from eth_bb.index.fs import FsIndex
from eth_bb.store.date import Store as FsDateStore
from eth_bb.util import clean

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

hash_of_foo = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'


block_src= '{"author": "0x5c5ab0d602eef41f82b6fc087a24e61383589c39", "baseFeePerGas": "0x7", "base_fee_per_gas": "0x7", "difficulty": "0xfffffffffffffffffffffffffffffffe", "extraData": "0xdb830303038c4f70656e457468657265756d86312e34372e30826c69", "extra_data": "0xdb830303038c4f70656e457468657265756d86312e34372e30826c69", "gasLimit": "0x989680", "gas_limit": "0x989680", "gasUsed": "0x104c2", "gas_used": "0x104c2", "hash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "logsBloom": "0x00000000000000010000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000020000000000000000000800000000000000000000000000000000000000000000000000001000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000020000000002000000000000000000000000000000010000040000000000000000000", "logs_bloom": "0x00000000000000010000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000020000000000000000000800000000000000000000000000000000000000000000000000001000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000020000000002000000000000000000000000000000010000040000000000000000000", "miner": "0x5c5ab0d602eef41f82b6fc087a24e61383589c39", "number": "0x4d32e", "parentHash": "0xaf92787ea9aa80c231f575bfe0ab9070d2246e2c5c6623f3a90f42681099ea5d", "parent_hash": "0xaf92787ea9aa80c231f575bfe0ab9070d2246e2c5c6623f3a90f42681099ea5d", "receiptsRoot": "0xfeb41fce406bc9f75497d282d56adc05262d0ab7803104d6ff46de0a636bfd7d", "receipts_root": "0xfeb41fce406bc9f75497d282d56adc05262d0ab7803104d6ff46de0a636bfd7d", "sealFields": ["0x8410ce6f23", "0xb8419d7f260372f974246ddc7eeba28dd6038edf09da8ad4607a3d1810246563e456710865eb657ca1ebf992111f4101bf2e2321ec0ada9214305f47965d0469ddec01"], "seal_fields": ["0x8410ce6f23", "0xb8419d7f260372f974246ddc7eeba28dd6038edf09da8ad4607a3d1810246563e456710865eb657ca1ebf992111f4101bf2e2321ec0ada9214305f47965d0469ddec01"], "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347", "sha3_uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347", "signature": "9d7f260372f974246ddc7eeba28dd6038edf09da8ad4607a3d1810246563e456710865eb657ca1ebf992111f4101bf2e2321ec0ada9214305f47965d0469ddec01", "size": "0x2f9", "stateRoot": "0x21ec56d85f554820fffef4b0f03197867cfc3f54188689b45baa85f394194543", "state_root": "0x21ec56d85f554820fffef4b0f03197867cfc3f54188689b45baa85f394194543", "step": "281964323", "timestamp": "0x64d69ad2", "totalDifficulty": "0x4d32dffffffffffffffffffffffffef2cbdb1", "total_difficulty": "0x4d32dffffffffffffffffffffffffef2cbdb1", "transactions": [{"blockHash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "blockNumber": "0x4d32e", "chainId": "0x13ba", "condition": null, "creates": null, "from": "0xeb3907ecad74a0013c259d5874ae7f22dcbcc95c", "gas": "0x7a120", "gasPrice": "0x8", "hash": "0x7d13637fa09da3137f1081b46f3393341141902be14c465ac7d0568c8a199479", "input": "0xd1de592a00000000000000000000000000000000000000000000000000000000000000002c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae", "nonce": "0xe6a0", "publicKey": "0x9f6bb6a7e3f5b7ee71756a891233d1415658f8712bac740282e083dc9240f5368bdb3b256a5bf40a8f7f9753414cb447ee3f796c5f30f7eb40a7f5018fc7f02e", "r": "0x7841ef907c03019d1052492b8bfa5e040309bcacfb97039367878cae8b522110", "raw": "0xf8a982e6a0088307a12094604e705e0cd2d077ab56aabebf29c105050a1c8a80b844d1de592a00000000000000000000000000000000000000000000000000000000000000002c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae822797a07841ef907c03019d1052492b8bfa5e040309bcacfb97039367878cae8b522110a02ff9c8e6fd3f93450d566ef8c7fe68ce0bb94ac08dadb6be8f70377c1dfbf0b4", "s": "0x2ff9c8e6fd3f93450d566ef8c7fe68ce0bb94ac08dadb6be8f70377c1dfbf0b4", "standardV": "0x0", "to": "0x604e705e0cd2d077ab56aabebf29c105050a1c8a", "transactionIndex": "0x0", "type": "0x0", "v": "0x2797", "value": "0x0"}], "transactionsRoot": "0x84e46a580785856ee05da3bb7542595cb8bee932148e3f85d96244d9e30fb8bd", "transactions_root": "0x84e46a580785856ee05da3bb7542595cb8bee932148e3f85d96244d9e30fb8bd", "uncles": [], "gas_price": "0x0"}'

tx_src = '{"blockHash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "block_hash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "blockNumber": "0x4d32e", "block_number": "0x4d32e", "chainId": "0x13ba", "chain_id": "0x13ba", "condition": null, "creates": null, "from": "0xeb3907ecad74a0013c259d5874ae7f22dcbcc95c", "gas": "0x7a120", "gasPrice": "0x8", "gas_price": "0x8", "hash": "0x7d13637fa09da3137f1081b46f3393341141902be14c465ac7d0568c8a199479", "input": "0xd1de592a00000000000000000000000000000000000000000000000000000000000000002c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae", "nonce": "0xe6a0", "publicKey": "0x9f6bb6a7e3f5b7ee71756a891233d1415658f8712bac740282e083dc9240f5368bdb3b256a5bf40a8f7f9753414cb447ee3f796c5f30f7eb40a7f5018fc7f02e", "public_key": "0x9f6bb6a7e3f5b7ee71756a891233d1415658f8712bac740282e083dc9240f5368bdb3b256a5bf40a8f7f9753414cb447ee3f796c5f30f7eb40a7f5018fc7f02e", "r": "0x7841ef907c03019d1052492b8bfa5e040309bcacfb97039367878cae8b522110", "raw": "0xf8a982e6a0088307a12094604e705e0cd2d077ab56aabebf29c105050a1c8a80b844d1de592a00000000000000000000000000000000000000000000000000000000000000002c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae822797a07841ef907c03019d1052492b8bfa5e040309bcacfb97039367878cae8b522110a02ff9c8e6fd3f93450d566ef8c7fe68ce0bb94ac08dadb6be8f70377c1dfbf0b4", "s": "0x2ff9c8e6fd3f93450d566ef8c7fe68ce0bb94ac08dadb6be8f70377c1dfbf0b4", "standardV": "0x0", "standard_v": "0x0", "to": "0x604e705e0cd2d077ab56aabebf29c105050a1c8a", "transactionIndex": "0x0", "transaction_index": "0x0", "type": "0x0", "v": 10135, "value": "0x0"}'

rcpt_src = '{"blockHash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "block_hash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "blockNumber": "0x4d32e", "block_number": "0x4d32e", "contractAddress": null, "contract_address": null, "cumulativeGasUsed": "0x104c2", "cumulative_gas_used": "0x104c2", "effectiveGasPrice": "0x8", "effective_gas_price": "0x8", "from": "0xeb3907ecad74a0013c259d5874ae7f22dcbcc95c", "gasUsed": "0x104c2", "gas_used": "0x104c2", "logs": [{"address": "0x604e705e0cd2d077ab56aabebf29c105050a1c8a", "blockHash": "0x58f0d224536e2925db01dabb28f63e597f6065da36375b7cccc9b2dc25c1b084", "blockNumber": "0x4d32e", "data": "0x2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae", "logIndex": "0x0", "removed": false, "topics": ["0x41773ccda7d0480f465faa57e86ce7b76c501e146b4f69001f43619d5bc5f60a", "0x000000000000000000000000eb3907ecad74a0013c259d5874ae7f22dcbcc95c", "0x0000000000000000000000000000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000000000000000000000000000"], "transactionHash": "0x7d13637fa09da3137f1081b46f3393341141902be14c465ac7d0568c8a199479", "transactionIndex": "0x0", "transactionLogIndex": "0x0", "type": "mined"}], "logsBloom": "0x00000000000000010000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000020000000000000000000800000000000000000000000000000000000000000000000000001000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000020000000002000000000000000000000000000000010000040000000000000000000", "logs_bloom": "0x00000000000000010000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000020000000000000000000800000000000000000000000000000000000000000000000000001000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000020000000002000000000000000000000000000000010000040000000000000000000", "status": "0x1", "to": "0x604e705e0cd2d077ab56aabebf29c105050a1c8a", "transactionHash": "0x7d13637fa09da3137f1081b46f3393341141902be14c465ac7d0568c8a199479", "transaction_hash": "0x7d13637fa09da3137f1081b46f3393341141902be14c465ac7d0568c8a199479", "transactionIndex": "0x0", "transaction_index": "0x0", "type": "0x0"}'


class TestFilter(EthTesterCase):

    def setUp(self):
        super(TestFilter, self).setUp()
        o = json.loads(block_src)
        self.block = Block.from_src(o)
        o = json.loads(tx_src)
        self.tx = Tx.from_src(o)
        o = json.loads(rcpt_src)
        self.tx.apply_receipt(o)

        self.author = strip_0x(self.tx.outputs[0])
        #self.topic = hash_of_foo
        self.topic = '00' * 32
        self.time = datetime.datetime.fromtimestamp(self.block.timestamp)


    def test_(self):
        ctx = None
        fltr = Filter()
        fltr.prepare(ctx)
        r = fltr.filter(self.rpc, self.block, self.tx, ctx=ctx)
        self.assertFalse(r)

        dp = tempfile.mkdtemp()
        idx = FsIndex(dp, 'test')
        r = idx.next(self.author, self.topic)
        self.assertIsNone(r)
        shutil.rmtree(dp)

        dp = tempfile.mkdtemp()
        fltr = Filter()
        ctx = {'usr': {'bbindex': 'fs', 'bbpath': dp}}
        fltr.prepare(ctx)
        r = fltr.filter(self.rpc, self.block, self.tx, ctx=ctx)
        fltr.stop()

        idx = FsIndex(dp, 'test')
        r = idx.next(self.author, self.topic)
        self.assertIsNotNone(r)
        shutil.rmtree(dp)


    def test_resolve(self):
        dp = tempfile.mkdtemp()
        ctx = {'usr': { 'bbresolver': 'eth_bb.unittest.resolve', 'bbindex': 'fs', 'bbpath': dp} }
        fltr = Filter()
        fltr.prepare(ctx)
        r = fltr.filter(self.rpc, self.block, self.tx, ctx=ctx)
        self.assertFalse(r)
        fltr.stop()
        shutil.rmtree(dp)
        o = {
                hash_of_foo: {
                    'author': self.author,
                    'topic': self.topic,
                    'time': self.time,
                    'content': 'foo',
                    }
                }
        self.assertDictEqual(fltr.contents, o)


    def test_resolve_history(self):
        dp = tempfile.mkdtemp()
        ctx = {'usr': {'bbindex': 'fs', 'bbpath': dp} }
        fltr = Filter()
        fltr.prepare(ctx)
        r = fltr.filter(self.rpc, self.block, self.tx, ctx=ctx)
        self.assertFalse(r)

        alice = os.urandom(20)
        alice_hex = alice.hex()
        o = json.loads(tx_src)
        tx_two = Tx.from_src(o)
        tx_two.outputs[0] = alice_hex
        o = json.loads(rcpt_src)
        tx_two.apply_receipt(o)
        r = fltr.filter(self.rpc, self.block, tx_two, ctx=ctx)
        self.assertFalse(r)
        fltr.stop()

        ctx = {'usr': { 'bbresolver': 'eth_bb.unittest.resolve', 'bbindex': 'fs', 'bbpath': dp} }
        fltr = Filter()
        fltr.prepare(ctx)
        fltr.stop()


    def test_store(self):
        dp = tempfile.mkdtemp()
        ctx = {'usr': { 'bbresolver': 'eth_bb.unittest.resolve', 'bbindex': 'fs', 'bbpath': dp, 'bbstore': 'fs'} }
        fltr = BaseFilter()
        fltr.prepare(ctx)
        r = fltr.filter(self.rpc, self.block, self.tx, ctx=ctx)
        self.assertFalse(r)
        fltr.stop()

        (author, topic, hsh, time) = clean(self.author, self.topic)
        t = self.time.strftime('%Y%m%d')
        fp = os.path.join(dp, '.content', author, topic, t)
        f = open(fp, 'r')
        r = f.read()
        f.close()

        cs = FsDateStore(dp) 
        expect = cs.render(self.author, self.topic, None, self.time, 'foo')
        self.assertEqual(r, expect)


    def test_store_reverse(self):
        dp = tempfile.mkdtemp()
        ctx = {'usr': { 'bbresolver': 'eth_bb.unittest.resolve', 'bbindex': 'fs', 'bbpath': dp, 'bbstore': 'fs_prepend'} }
        fltr = BaseFilter()
        fltr.prepare(ctx)
        r = fltr.filter(self.rpc, self.block, self.tx, ctx=ctx)
        self.assertFalse(r)
        fltr.stop()

        (author, topic, hsh, time) = clean(self.author, self.topic)
        t = self.time.strftime('%Y%m%d')
        fp = os.path.join(dp, '.content', author, topic, t)
        f = open(fp, 'r')
        r = f.read()
        f.close()

        cs = FsDateStore(dp) 
        expect = cs.render(self.author, self.topic, None, self.time, 'foo')
        self.assertEqual(r, expect)

       
if __name__ == '__main__':
    unittest.main()
