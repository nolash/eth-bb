# external imports
import feedparser
import logging
import datetime
import tempfile
import sys
import os

# local imports
from eth_bb.error import VerifyError
from eth_bb.render import Renderer

logg = logging.getLogger(__name__)


def verify(v):
    r = feedparser.parse(v)
    if len(r['entries']) == 0:
        raise VerifyError('No RSS entry found in file {}'.format(v))
    if len(r['entries']) > 1:
        raise VerifyError('More than one RSS entry found in file {}'.format(v))
    logg.info('RSS content verified in file {}'.format(v))


def verify_file(v):
    return verify(v)


class Builder(Renderer):

    def __init__(self, enable_verify):
        self.channel = 'eth-bb'
        self.title = 'ETH-BB vanilla render'
        self.date = datetime.datetime.utcnow()
        self.buf = []
        self.verify = enable_verify

    def write(self, v):
        try:
            verify(v)
            self.buf.append(v)
        except VerifyError as e:
            if self.verify:
                raise e
        return len(v)


    def flush(self, w=sys.stdout):
        for v in self.buf:
            w.write(v)
