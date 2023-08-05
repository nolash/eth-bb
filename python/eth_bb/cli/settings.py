# standard imports
import hashlib
import logging

logg = logging.getLogger(__name__)


def process_settings_local(settings, config):
    if config.get('_MIME') != None:
        h = hashlib.sha256()
        b = bytes.fromhex(config.get('_CONTEXT'))
        h.update(b)
        s = '.' + config.get('_MIME')
        b = s.encode('utf-8')
        h.update(b)
        settings.set('CONTEXT', h.digest().hex())
    else:
        settings.set('CONTEXT', config.get('_CONTEXT'))
    logg.debug('using context {}'.format(settings.get('CONTEXT')))
    return settings
