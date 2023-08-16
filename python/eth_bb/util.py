# external imports
from hexathon import strip_0x
from hexathon import uniform


def clean(author, topic, hsh=None, time=None):
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
