# standard imports
import importlib
import logging

logg = logging.getLogger(__name__)


def module_for(v):
    if v[:4] == 'http':
        return importlib.import_module('eth_bb.resolve.http')
    m = None
    try:
        m = importlib.import_module(v)
    except ModuleNotFoundError:
        pass
    return m
