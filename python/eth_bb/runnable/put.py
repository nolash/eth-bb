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
from eth_bb.cli.config import process_config_local
from eth_bb.cli.settings import process_settings_local
from eth_bb.render import RenderMode

logg = logging.getLogger()


def verify(config, v):
    if config.get('_MIME') == None:
        logg.debug('skipping verify since mime is not specified')
        return
    from eth_bb.render import mode_for
    from eth_bb.error import VerifyError
    mime = config.get('_MIME')
    mode = mode_for(mime)
    m = None
    if mode == None:
        raise VerifyError('verifier not found for content type "{}"'.format(mime))
    if mode == RenderMode.RSS:
        import importlib
        m = importlib.import_module('eth_bb.render.rss')
        m.verify_file(v)


def process_config_local_bb(config, arg, args, flags):
    if args.file != None:
        if args.verify:
            verify(config, args.file)
        f = open(args.file, 'rb')
        h = hashlib.sha256()
        while True:
            data = f.read(4096)
            if not data:
                break
            h.update(data)
        config.add(h.digest().hex(), '_CONTENT', False)
    elif args.digest != None:
        d = strip_0x(args.digest[0])
        assert len(d) == 64
        config.add(args.digest[0], '_CONTENT', False)
    return config


def process_settings_local_bb(settings, config):
    settings.set('CONTENT', config.get('_CONTENT'))
    return settings


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.EXEC | arg_flags.WALLET

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('--topic', type=str, default=ZERO_CONTENT, help='topic in 0x-prefixed hex or plain string')
argparser.add_argument('--mime', type=str, help='post mime type')
argparser.add_argument('--mode', type=str, help='human-friendly mime definition')
argparser.add_argument('--file', type=str, help='create digest from file')
argparser.add_argument('--verify', action='store_true', help='verify contents against mime type')
argparser.add_argument('digest', type=str, nargs='*', help='content digest to post')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags)
config = process_config_local(config, arg, args, flags)
config = process_config_local_bb(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
settings = process_settings_local(settings, config)
settings = process_settings_local_bb(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    contract_address = settings.get('EXEC')
    signer_address = settings.get('SENDER_ADDRESS')
    topic = settings.get('TOPIC')
    content = settings.get('CONTENT')
    conn = settings.get('CONN')
    c = BB(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )

    (tx_hash_hex, o) = c.add(contract_address, signer_address, content, topic=topic, id_generator=settings.get('RPC_ID_GENERATOR'))
    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                logg.critical('VM revert. Wish I could tell you more')
                sys.exit(1)
        print(tx_hash_hex)

    else:
        print(o['params'][0])


if __name__ == '__main__':
    main()
