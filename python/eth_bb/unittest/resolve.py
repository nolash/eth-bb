# standard imports
import logging

hash_of_foo = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'

logg = logging.getLogger(__name__)


def resolve(endpoint, v):
    logg.debug('unittest resolve resolving {}'.format(v))
    if  v == hash_of_foo:
        return 'foo'
    return ''
