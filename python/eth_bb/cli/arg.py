# standard imports
import hashlib
import logging

# external imports
from hexathon import strip_0x

logg = logging.getLogger(__name__)


def arg_hsh(v):
    h = hashlib.sha256()
    h.update(v.encode('utf-8'))
    z = h.digest()
    r = z.hex()
    logg.info('topic {} -> digest {}'.format(v, r))
    return r


def arg_to_topic(v):
    if len(v) < 2:
        return arg_hsh(v)
    if v[:2] == '0x':
        if len(v) != 66:
            raise ValueError('hex valud must represent 32 bytes')
        return v
    return arg_hsh(v)

