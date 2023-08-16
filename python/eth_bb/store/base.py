# external imports
from hexathon import uniform


def noop(topic, author, hsh, time, content):
    return content


class Store:

    def __init__(self, renderer=noop, reverse=False):
        self.reverse = reverse
        self.render = renderer
        if self.render == None:
            self.render = noop


    def put(self, author, topic, hsh, time, content, render=True):
        raise NotImplementedError()
