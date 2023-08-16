# standard imports
import os
import logging
import shutil
import tempfile

# local imports
from .base import Store as BaseStore

logg = logging.getLogger(__name__)


class Store(BaseStore):

    def __init__(self, path, limit, index_filename='index.txt', renderer=None, reverse=False):
        super(Store, self).__init__(renderer=renderer, reverse=reverse)
        self.size_limit = limit
        self.path = path
        self.index_filename = index_filename


    def put(self, author, topic, hsh, time, content, render=True):
        dp = os.path.join(self.path, author, topic)
        os.makedirs(dp, exist_ok=True)
        fp = os.path.join(dp, self.index_filename)
        r = content
        if render:
            r = self.render(author, topic, hsh, time, content)
        if self.reverse:
            return self.__store_prepend(fp, r)
        return self.__store_append(fp, r)


    def __store_prepend(self, fp, data):
        bdata = data.encode('utf-8')
        sz_add = len(bdata)
        sz_remaining = self.size_limit - sz_add

        xfp = '.' + self.index_filename + '.idx' 
        dp = os.path.dirname(fp)
        xfp = os.path.join(dp, xfp)
        fx = None
        try:
            fx = open(xfp, 'rb')
        except FileNotFoundError:
            fx = open(xfp, 'wb')
            fx.write(b'00' * 4)
            fx.close()
            fx = open(xfp, 'rb')

        idxb = b''
        while True:
            r = fx.read()
            if len(r) == 0:
                break
            idxb += r

        fx.close()
        (tyfd, tyfp) = tempfile.mkstemp()
        fy = os.fdopen(tyfd, 'wb')
        c = 0
        fy.write(b'\x00' * 4)

        l = len(idxb)
        v = 0
        for i in range(0, l, 4):
            c = int.from_bytes(idxb[i:i+4], byteorder='big')
            vp = v
            v = sz_add + c
            if v > sz_remaining:
                idxc = int(l / 4)
                i = int(i / 4)
                logg.info('ring store cutoff at entry {}/{} byte {}'.format(i, idxc, vp))
                break
            b = v.to_bytes(4, byteorder='big')
            fy.write(b)
        fy.close()

        (tfd, tfp) = tempfile.mkstemp()
        fo = os.fdopen(tfd, 'wb')
        fo.write(bdata) # write new data

        # TODO: merge with prepend date method, acept length limit
        try:
            fi = open(fp, 'rb')
        except FileNotFoundError:
            fi = open(fp, 'wb')
            fi.close()
            fi = open(fp, 'rb')

        while True:
            r = fi.read(c)
            if len(r) == 0:
                break
            c -= len(r)
            fo.write(r)

        fo.close()
        fi.close()

        # TODO: needs to be locked
        shutil.copy(tyfp, xfp)
        shutil.copy(tfp, fp)

        
    def __store_append(self, fp, data):
        bdata = data.encode('utf-8')
        sz_add = len(bdata)
        sz_remaining = self.size_limit - sz_add

        xfp = '.' + self.index_filename + '.idx' 
        dp = os.path.dirname(fp)
        xfp = os.path.join(dp, xfp)
        fx = None
        try:
            fx = open(xfp, 'rb')
        except FileNotFoundError:
            fx = open(xfp, 'wb')
            fx.close()
            fx = open(xfp, 'rb')

        idxb = b''
        while True:
            r = fx.read()
            if len(r) == 0:
                break
            idxb += r

        fx.close()

        (tyfd, tyfp) = tempfile.mkstemp()
        fy = os.fdopen(tyfd, 'wb')
        idxb = b'\x00' * 4
        fy.write(idxb)
        c = 0
        i = 0

        l = len(idxb)
        sz_existing = 0
        try:
            st = os.stat(fp)
            sz_existing = st.st_size
        except FileNotFoundError:
            pass

        for i in range(0, l, 4):
            c = int.from_bytes(idxb[i:i+4], byteorder='big')
            if sz_existing - c <= sz_remaining:
                break

        for j in range(i * 4, l ,4):
            v = int.from_bytes(idxb[j:j+4], byteorder='big')
            v -= c
            b = v.to_bytes(4, byteorder='big')
            fy.write(b)

        v = sz_existing - c
        b = v.to_bytes(4, byteorder='big')
        fy.write(b)
        fy.close()

        (tfd, tfp) = tempfile.mkstemp()
        fo = os.fdopen(tfd, 'wb')

        # TODO: merge with prepend date method, acept length limit
        try:
            fi = open(fp, 'rb')
        except FileNotFoundError:
            fi = open(fp, 'wb')
            fi.close()
            fi = open(fp, 'rb')
        
        fi.seek(v)
        while True:
            r = fi.read()
            if len(r) == 0:
                break
            c -= len(r)
            fo.write(r)

        fo.write(bdata) # write new data
        fo.close()
        fi.close()

        # TODO: needs to be locked
        shutil.copy(tyfp, xfp)
        shutil.copy(tfp, fp)
