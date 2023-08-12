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
        self.reverse_author = {}
        self.reverse_topic = {}

    
    def add(self, time, author, topic, hsh, ctx):
        if self.contents.get(author, None) == None:
            self.contents[author] = {}
        if self.contents[author].get(topic, None) == None:
            self.contents[author] = {
                    topic: [],
                    }
        self.reverse_author[hsh] = author
        self.reverse_topic[hsh] = topic
        self.resolve(hsh)


    def store_item(self, content, hsh):
        author = self.reverse_author[hsh]
        topic  = self.reverse_topic[hsh]
        o = {
                'hash': hsh,
                'content': content,
                }
        self.contents[author][topic].append(o)
