# standard imports
import os
import logging

# external imports
from chainlib.eth.tx import TxFormat
from chainlib.eth.tx import TxFactory
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.constant import ZERO_CONTENT
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.eth.contract import ABIContractEncoder
from chainlib.eth.contract import ABIContractType
from hexathon import strip_0x
from hexathon import add_0x

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')

logg = logging.getLogger(__name__)


class BB(TxFactory):

    __abi = None
    __bytecode = None

    @staticmethod
    def abi():
        if BB.__abi == None:
            f = open(os.path.join(datadir, 'BB.json'), 'r')
            BB.__abi = json.load(f)
            f.close()
        return BB.__abi


    @staticmethod
    def bytecode(version=None):
        if BB.__bytecode == None:
            f = open(os.path.join(datadir, 'BB.bin'))
            BB.__bytecode = f.read()
            f.close()
        return BB.__bytecode


    @staticmethod
    def gas(code=None):
        return 4000000


    def constructor(self, sender_address, tx_format=TxFormat.JSONRPC, version=None):
        code = self.cargs(version=version)
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.finalize(tx, tx_format)


    @staticmethod
    def cargs(version=None):
        return BB.bytecode()


    def add(self, contract_address, sender_address, content, topic=ZERO_CONTENT, tx_format=TxFormat.JSONRPC, id_generator=None):
        enc = ABIContractEncoder()
        enc.method('add')
        enc.typ(ABIContractType.BYTES32)
        enc.typ(ABIContractType.BYTES32)
        enc.bytes32(topic)
        enc.bytes32(content)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format, id_generator=id_generator)
        return tx


    def entry(self, contract_address, author_address, idx, topic=ZERO_CONTENT, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('entry')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.BYTES32)
        enc.typ(ABIContractType.UINT256)
        enc.address(author_address)
        enc.bytes32(topic)
        enc.uint256(idx)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def entry_count(self, contract_address, author_address, topic, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('entryCount')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.BYTES32)
        enc.address(author_address)
        enc.bytes32(topic)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


def bytecode(**kwargs):
    return BB.bytecode(version=kwargs.get('version'))


def args(v):
    if v == 'default' or v == 'bytecode':
        return ([], ['version'],)
    raise ValueError('unknown command: ' + v)
