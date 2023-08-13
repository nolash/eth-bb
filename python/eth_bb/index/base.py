# external imports
from hexathon import strip_0x
from hexathon import uniform


class Index():

    def __init__(self):
        self.crsr = 0
        self.step = 1
        self.__iter_authors = None
        self.__iter_topics = None


    def clean(self, author, topic, hsh=None, time=None):
        if hsh != None:
            hsh = strip_0x(hsh)
            if len(hsh) != 64:
                raise ValueError('hash must be 32 bytes')
            hsh = uniform(hsh)
        topic = strip_0x(topic)
        if len(topic) != 64:
            raise ValueError('topic must be 32 bytes')
        topic = uniform(topic)
        author = strip_0x(author)
        if len(author) != 40:
            raise ValueError('topic must be 20 bytes')
        author = uniform(author)
        return (author, topic, hsh, time,)


    def put(self, author, topic, hsh, time):
        return None


    def next(self):
        return None


    def __iter__(self):
        self.iter_authors = []
        for v in self.authors():
            self.iter_authors.append(v)
        if len(self.iter_authors) > 0:
            self.iter_topics = self.topics(self.iter_authors[0])
        return self


    def __next__(self):
        if self.iter_authors == None:
            raise StopIteration()
        topic = None
        try:
            topic = self.iter_topics.pop(0)
        except IndexError:
            self.iter_topics = None
        except AttributeError:
            self.iter_topics = None
        if self.iter_topics == None:
            try:
                self.iter_authors.pop(0)
            except IndexError:
                raise StopIteration()
            try:
                self.iter_topics = self.topics(self.iter_authors[0])
            except IndexError:
                raise StopIteration()
        author = self.iter_authors[0]
        if topic == None:
            topic = self.iter_topics.pop(0)
        return (author, topic,)
