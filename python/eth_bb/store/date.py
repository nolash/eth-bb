# standard imports
import os


class FsDateStore:

    def __init__(self, path, renderer=None):
        self.path = path
        if renderer == None:
            renderer = self.__renderer
        self.render = renderer


    def put(self, author, topic, hsh, time, content):
        dp = os.path.join(self.path, author)
        os.makedirs(dp, exist_ok=True)
        fp = os.path.join(dp, topic)
        r = self.render(author, topic, hsh, time, content)
        f = open(fp, 'a')
        f.write(r)
        f.close()


    def __renderer(self, author, topic, hsh, time, content):
        return '[{}]\n\n{}\n---\n\n'.format(time, content)
