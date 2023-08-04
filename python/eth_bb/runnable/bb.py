#!python3

"""Token transfer script

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import os
import io
import json
import argparse
import logging
import hashlib

# external imports
from hexathon import (
        add_0x,
        strip_0x,
        )
import chainlib.eth.cli
from chainlib.eth.cli.log import process_log
from chainlib.eth.constant import ZERO_CONTENT
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings
from chainlib.eth.cli.arg import (
        Arg,
        ArgFlag,
        process_args,
        )
from chainlib.eth.cli.config import (
        Config,
        process_config,
        )

# local imports
from eth_bb import BB

logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    config.add(args.mime, '_MIME', False)
    config.add(strip_0x(args.context), '_CONTEXT', False)
    if args.file != None:
        f = open(args.file, 'rb')
        h = hashlib.sha256()
        while True:
            data = f.read(4096)
            if not data:
                break
            h.update(data)
        config.add(h.digest().hex(), '_CONTENT', False)
    else:
        d = strip_0x(args.digest[0])
        assert len(d) == 64
        config.add(args.digest[0], '_CONTENT', False)
    return config


def process_settings_local(settings, config):
    if config.get('_MIME') != None:
        h = hashlib.sha256()
        b = bytes.fromhex(config.get('_CONTEXT'))
        h.update(b)
        s = '.' + config.get('_MIME')
        b = s.encode('utf-8')
        h.update(b)
        settings.set('CONTEXT', h.digest().hex())
    else:
        settings.set('CONTEXT', config.get('_CONTEXT'))
    settings.set('CONTENT', config.get('_CONTENT'))
    logg.debug('using context {}'.format(settings.get('CONTEXT')))
    return settings


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.EXEC | arg_flags.WALLET


argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('--context', type=str, default=ZERO_CONTENT, help='name of context')
argparser.add_argument('--mime', type=str, help='post mime type')
argparser.add_argument('--file', type=str, help='create digest from file')
argparser.add_argument('digest', type=str, nargs='*', help='content digest to post')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags) #, positional_name='value')
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
settings = process_settings_local(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    contract_address = settings.get('EXEC')
    signer_address = settings.get('SENDER_ADDRESS')
    ctx = settings.get('CONTENT')
    content = settings.get('CONTEXT')
    conn = settings.get('CONN')
    c = BB(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )

    (tx_hash_hex, o) = c.add(contract_address, signer_address, ctx, content, id_generator=settings.get('RPC_ID_GENERATOR'))
    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if logg.isEnabledFor(logging.DEBUG):
                sender_balance = balance(conn, g, token_address, signer_address, id_generator=settings.get('RPC_ID_GENERATOR'))
                recipient_balance = balance(conn, g, token_address, recipient, id_generator=settings.get('RPC_ID_GENERATOR'))
                logg.debug('sender {} balance after: {}'.format(signer_address, sender_balance))
                logg.debug('recipient {} balance after: {}'.format(recipient, recipient_balance))
            if r['status'] == 0:
                logg.critical('VM revert. Wish I could tell you more')
                sys.exit(1)
        print(tx_hash_hex)

    else:
        print(o['params'][0])


if __name__ == '__main__':
    main()
