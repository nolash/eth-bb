# standard imports
import os
import logging
import shutil
import tempfile

logg = logging.getLogger(__name__)


class Store:

    def __init__(self, path, reverse=False, renderer=None):
        self.path = path
        self.reverse = reverse
        if renderer == None:
            renderer = self.__renderer
        self.render = renderer


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
        logg.debug('prepended content to {}'.format(fp))


    def __store_append(self, fp, data):
        f = open(fp, 'a')
        f.write(data)
        f.close()
        logg.debug('appended content to {}'.format(fp))


    def put(self, author, topic, hsh, time, content):
        dp = os.path.join(self.path, author, topic)
        os.makedirs(dp, exist_ok=True)
        t = time.strftime('%Y%m%d')
        fp = os.path.join(dp, t)
        r = self.render(author, topic, hsh, time, content)
        if self.reverse:
            return self.__store_prepend(fp, r)
        return self.__store_append(fp, r)


    def __renderer(self, author, topic, hsh, time, content):
        return '[{}]\n\n{}\n---\n\n'.format(time, content)
