"""
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
import sys

# external imports
from hexathon import (
        add_0x,
        strip_0x,
        )
import chainlib.eth.cli
from chainlib.eth.cli.log import process_log
from chainlib.eth.cli.arg import stdin_arg
from chainlib.eth.constant import ZERO_CONTENT
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings
from chainlib.jsonrpc import JSONRPCException
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

def process_config_local_get(config, arg, args, flags):
    config.add(bool(args.reverse), '_REVERSE', False)
    config.add(args.offset, '_OFFSET', False)
    config.add(args.limit, '_LIMIT', False)

    author = config.get('_POSARG')
    try:
        author = strip_0x(author)
    except TypeError:
        author = stdin_arg()
        author = strip_0x(author)

    config.add(author, '_AUTHOR', False)
    config.add(args.resolve, '_RESOLVE', False)
    config.add(args.resolve_module, '_RESOLVE_MODULE', False)
    config.add(args.render, '_RENDER', False)
    config.add(args.render_module, '_RENDER_MODULE', False)
    return config


def process_settings_local_get(settings, config):
    settings.set('AUTHOR', config.get('_AUTHOR'))
    settings.set('RESOLVER', None)

    resolve = config.get('_RESOLVE')
    if resolve != None:
        import eth_bb.resolve
        settings.set('RESOLVER_SPEC', resolve)
        m = None
        if config.get('_RESOLVE_MODULE') != None:
            import importlib
            m = importlib.import_module(config.get('_RESOLVE_MODULE'))
        else:
            m = eth_bb.resolve.module_for(resolve)
        settings.set('RESOLVER', m)

    if config.true('_RENDER'):
        m = None
        if config.get('_RENDER_MODULE'):
            import importlib
            m = importlib.import_module(config.get('_RENDER_MODULE'))
        else:
            from eth_bb.render import mode_for
            mime = config.get('_MIME')
            mode = mode_for(mime)
            if mode == None:
                raise VerifyError('verifier not found for content type "{}"'.format(mime))
            if mode == RenderMode.RSS:
                import importlib
                m = importlib.import_module('eth_bb.render.rss')
        settings.set('RENDERER', m.Builder(settings.get('VERIFY')))
    return settings


def resolve(settings, v, w=sys.stdout):
    if settings.get('RESOLVER') == None:
        w.write(v + "\n")
        return
    r = settings.get('RESOLVER').resolve(settings.get('RESOLVER_SPEC'), v)
    w.write(r + "\n")

def render(settings, v, w=sys.stdout):
    ww = w
    renderer = settings.get('RENDERER')
    if renderer != None:
        ww = renderer
    resolve(settings, v, w=ww)
    if renderer != None:
        renderer.flush(w=w)


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.EXEC | arg_flags.WALLET

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('--context', type=str, default=ZERO_CONTENT, help='name of context')
argparser.add_argument('--mime', type=str, help='post mime type, overrides')
argparser.add_argument('--mode', type=str, help='human-friendly mime definition')
argparser.add_argument('--offset', type=int, default=0, help='start index')
argparser.add_argument('--limit', type=int, default=0, help='end index')
argparser.add_argument('--reverse', action='store_true', help='return values in reverse sequential order')
argparser.add_argument('--resolve', type=str, help='spec to resolve the content hashes to content')
argparser.add_argument('--resolve-module', dest='resolve_module', type=str, help='module to use for resolving. overrides builtin modules')
argparser.add_argument('--render', action='store_true', help='render the result according to the given mime type')
argparser.add_argument('--render-module', dest='render_module', type=str, help='module to use for rendering')
argparser.add_argument('--verify', action='store_true', help='verify contents against mime type')
argparser.add_argument('author', type=str, nargs='*', help='return values in reverse sequential order')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags, positional_name='author')
config = process_config_local(config, arg, args, flags)
config = process_config_local_get(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
settings = process_settings_local(settings, config)
settings = process_settings_local_get(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    contract_address = settings.get('EXEC')
    conn = settings.get('CONN')
    sender_address = settings.get('SENDER_ADDRESS')
    c = BB(
            chain_spec=settings.get('CHAIN_SPEC'),
            gas_oracle=settings.get('GAS_ORACLE'),
            )

    count = 0
    offset = config.get('_OFFSET')
    limit = config.get('_LIMIT')
    step = 1 

    if config.get('_REVERSE'):
        o = c.entry_count(contract_address, settings.get('AUTHOR'), settings.get('CONTEXT'), sender_address=sender_address)
        r = conn.do(o)
        count = int(r, 16)
        offset = count - 1
        if limit == 0:
            limit = -1
        else:
            limit = offset - limit

        step = -1
    else:
        if limit == 0:
            o = c.entry_count(contract_address, settings.get('AUTHOR'), settings.get('CONTEXT'), sender_address=sender_address)
            r = conn.do(o)
            count = int(r, 16)
            limit = count
        limit = offset + limit
    
    logg.debug('have offset {} limit {} step {}'.format(offset, limit, step))
    for i in range(offset, limit, step):
        o = c.entry(contract_address, settings.get('AUTHOR'), i, ctx=settings.get('CONTEXT'), sender_address=sender_address)
        try:
            r = conn.do(o)
        except JSONRPCException:
            break
        
        render(settings, strip_0x(r))


if __name__ == '__main__':
    main()
