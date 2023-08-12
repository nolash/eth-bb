# local imports
from eth_bb.filter.base import Filter as BaseFilter


class Filter(BaseFilter):

    def __init__(self):
        super(Filter, self).__init__()
        self.contents = {}


    def store_item(self, content, hsh):
        self.contents[hsh] = content
