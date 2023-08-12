# standard imports
import os
import logging

logg = logging.getLogger(__name__)


class FsDateStore:

    def __init__(self, path, renderer=None):
        self.path = path
        if renderer == None:
            renderer = self.__renderer
        self.render = renderer


    def put(self, author, topic, hsh, time, content):
        dp = os.path.join(self.path, author, topic)
        os.makedirs(dp, exist_ok=True)
        t = time.strftime('%Y%m%d')
        fp = os.path.join(dp, t)
        r = self.render(author, topic, hsh, time, content)
        f = open(fp, 'a')
        f.write(r)
        f.close()
        logg.debug('appended content to {}'.format(fp))


    def __renderer(self, author, topic, hsh, time, content):
        return '[{}]\n\n{}\n---\n\n'.format(time, content)
