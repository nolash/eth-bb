# standard imports
import hashlib
import logging

# local imports
from eth_bb.cli.arg import arg_to_topic

logg = logging.getLogger(__name__)


def process_settings_local(settings, config):
    topic = arg_to_topic(config.get('_TOPIC'))
    if config.get('_MIME') != None:
        h = hashlib.sha256()
        b = bytes.fromhex(topic)
        h.update(b)
        s = '.' + config.get('_MIME')
        b = s.encode('utf-8')
        h.update(b)
        settings.set('TOPIC', h.digest().hex())
    else:
        settings.set('TOPIC', topic)
    logg.debug('using topic {}'.format(settings.get('TOPIC')))
    settings.set('VERIFY', config.true('_VERIFY'))
    return settings
