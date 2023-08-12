# standard imports
import os
import logging

# local imports
from eth_bb.filter.base import Filter as BaseFilter

logg = logging.getLogger(__name__)


class Filter(BaseFilter):

    index_size = 64+40+14

    def __init__(self):
        super(Filter, self).__init__()
        self.contents = {}

    
    def resolve_index_process(self, content, hsh):
        while True:
            r = None
            try:
                r = self.reverse[hsh].pop()
            except IndexError:
                break
            except KeyError:
                break
            self.store_item_for(r[0], r[1], r[2], content, hsh)
        self.reverse[hsh] = None


    def store_item(self, content, hsh):
        logg.debug('stored {} {}'.format(content, hsh))
