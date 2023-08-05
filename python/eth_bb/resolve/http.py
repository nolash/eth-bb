# standard imports
import urllib.request 
import urllib.error
import os
import logging

logg = logging.getLogger(__name__)


def resolve(endpoint, v):
    s = os.path.join(endpoint, v)
    rs = None
    try:
        rs = urllib.request.urlopen(s)
    except urllib.error.URLError as e:
        logg.error('content resolution failed for {}: {}'.format(v, e))
        return ''
    r = rs.read()
    return r.decode('utf-8')
