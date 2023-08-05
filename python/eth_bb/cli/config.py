# standard imports
import hashlib
import logging

# external imports
from hexathon import strip_0x

# local imports
from eth_bb.render import mode_to_mime

logg = logging.getLogger(__name__)


def process_config_local(config, arg, args, flags):
    if args.mode != None:
        mime = mode_to_mime(args.mode)
        config.add(mime, '_MIME', False)
    else:
        config.add(args.mime, '_MIME', False)
    config.add(strip_0x(args.context), '_CONTEXT', False)
    config.add(args.verify, '_VERIFY', False)
    return config 
