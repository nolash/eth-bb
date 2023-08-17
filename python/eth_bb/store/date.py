# standard imports
import os
import logging
import shutil
import tempfile

# local imports
from .base import Store as BaseStore
from eth_bb.util import clean

logg = logging.getLogger(__name__)


class Store(BaseStore):

    def __init__(self, path, renderer=None, reverse=False):
        if renderer == None:
            renderer = self.__defaultrenderer
        super(Store, self).__init__(renderer=renderer, reverse=reverse)
        self.path = path


    def __defaultrenderer(self, author, topic, hsh, time, content):
        return '[{}]\n\n{}\n---\n\n'.format(time, content)


    def __store_prepend(self, fp, data):
        (tfd, tfp) = tempfile.mkstemp()
        f = os.fdopen(tfd, 'w')
        f.write(data)
     
        data = ''
        try:
            ff = open(fp, 'r')
            while True:
                r = ff.read()
                if r == '':
                    break
                data += r
            ff.close()
        except FileNotFoundError:
            pass
        f.write(data)
        f.close()
        shutil.copy(tfp, fp)
        os.unlink(tfp)
        os.chmod(fp, 0o0644)
        logg.debug('prepended content to {}'.format(fp))


    def __store_append(self, fp, data):
        f = open(fp, 'a')
        f.write(data)
        f.close()
        os.chmod(fp, 0o0644)
        logg.debug('appended content to {}'.format(fp))


    def put(self, author, topic, hsh, time, content, render=True):
        (author, topic, hsh, time) = clean(author, topic, hsh, time)
        dp = os.path.join(self.path, author, topic)
        os.makedirs(dp, exist_ok=True)
        t = time.strftime('%Y%m%d')
        fp = os.path.join(dp, t)
        r = content
        if render:
            r = self.render(author, topic, hsh, time, content)
        if self.reverse:
            return self.__store_prepend(fp, r)
        return self.__store_append(fp, r)
