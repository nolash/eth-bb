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
        self.resolve(time, author, topic, hsh)


    def resolve_index_push(self, time, author, topic, hsh):
        time = time.strftime("%Y%m%d")
        o = (time, author, topic,)
        if self.reverse.get(hsh, None) == None:
            self.reverse[hsh] = []
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
            self.store_item_for(r[0], r[1], r[2], content, hsh)
        self.reverse[hsh] = None


    def store_item(self, content, hsh):
        author = self.reverse_author[hsh]
        topic  = self.reverse_topic[hsh]
        o = {
                'hash': hsh,
                'content': content,
                }
        self.contents[author][topic].append(o)
