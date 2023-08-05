# external imports
import feedparser
import logging

# local imports
from eth_bb.error import VerifyError

logg = logging.getLogger(__name__)


def verify_file(v):
    r = feedparser.parse(v)
    if len(r['entries']) == 0:
        raise VerifyError('No RSS entry found in file {}'.format(v))
    if len(r['entries']) > 1:
        raise VerifyError('More than one RSS entry found in file {}'.format(v))
    logg.info('RSS content verified in file {}'.format(v))


class Builder:
