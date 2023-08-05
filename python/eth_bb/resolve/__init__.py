# standard imports
import importlib

def module_for(v):
    if v[:4] == 'http':
        return importlib.import_module('eth_bb.resolve.http')
    return None
