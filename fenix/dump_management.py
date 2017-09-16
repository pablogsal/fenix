from __future__ import print_function

import gzip
import linecache
import sys
import types
import functools

import dill as pickle
import pdb

from fenix.wrappers import PhoenixTraceback, PhoenixCode, PhoenixFrame

__version__ = "1.1.1"

def iscode(object):
    return isinstance(object, (PhoenixCode,types.CodeType))

def isframe(object):
    return isinstance(object, (PhoenixFrame,types.FrameType))

def intercept_with_custom_types(func):
    @functools.wraps(func)
    def wrapper(obj):
        if hasattr(obj, "d_class") and obj.d_class == "frame":
            obj = obj.f_code
        return func(obj)

    return wrapper


def monkey_patch_inspect():
    import inspect
    inspect.findsource = intercept_with_custom_types(inspect.findsource)
    inspect.iscode = iscode
    inspect.isframe = isframe



def save_dump(filename, traceback=None):
    if traceback is None:
        traceback = sys.exc_info()[2]
    traceback = PhoenixTraceback(traceback)
    traceback.prepare_for_serialization()
    traceback_files = traceback.get_traceback_files()
    dump = {
        'traceback': traceback,
        'files': traceback_files,
    }
    with gzip.open(filename, 'wb') as f:
        pickle.dump(dump, f)


def load_dump(filename):
    with gzip.open(filename, 'rb') as f:
        return pickle.load(f)


def debug_dump(filename, post_mortem_func=pdb.post_mortem):
    monkey_patch_inspect()
    dump = load_dump(filename)
    _cache_files(dump['files'])
    tb = dump['traceback']
    tb.prepare_for_deserialization()
    _old_checkcache = linecache.checkcache
    linecache.checkcache = lambda filename=None: None
    post_mortem_func(tb)
    linecache.checkcache = _old_checkcache


def _cache_files(files):
    for name, data in files.items():
        lines = [line + '\n' for line in data.splitlines()]
        linecache.cache[name] = (len(data), None, lines, name)
