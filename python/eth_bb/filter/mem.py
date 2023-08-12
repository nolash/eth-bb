# standard imports
import os
import logging

# local imports
from eth_bb.filter.base import Filter as BaseFilter

logg = logging.getLogger(__name__)


class Filter(BaseFilter):

    def __init__(self):
        super(Filter, self).__init__()
        self.contents = {}
        self.reverse = {}

    
    def add(self, time, author, topic, hsh, ctx):
        if self.contents.get(author, None) == None:
            self.contents[author] = {}
        if self.contents[author].get(topic, None) == None:
            self.contents[author] = {
                    topic: [],
                    }
        self.resolve_index_push(time, author, topic, hsh, ctx)


    def resolve_index_push(self, time, author, topic, hsh, ctx):
        time = time.strftime("%Y%m%d")
        o = (topic, author, time,)
        self.reverse[hsh].append(o)


    def resolve_index_process(self, content, hsh):
        while True:
            r = None
            try:
                r = self.reverse[hsh].pop()
            except IndexError:
                break
            except KeyError:
                break
            self.store_item_for(r[1], r[0], r[2], content, hsh)


    def store_item(self, content, hsh):
        author = self.reverse_author[hsh]
        topic  = self.reverse_topic[hsh]
        o = {
                'hash': hsh,
                'content': content,
                }
        self.contents[author][topic].append(o)
