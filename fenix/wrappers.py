import os
import types

import six

from fenix.serializers import serialize_generic_obj, serializable

try:
    import builtins

    builtins_ = builtins.__dict__
except ImportError:
    builtins_ = __builtins__


class PhoenixMeta(type):
    mappings = {}

    def __new__(mcs, name, bases, kwargs):
        kwargs["_mappings"] = mcs.mappings
        cls = super(PhoenixMeta, mcs).__new__(mcs, name, bases, kwargs)
        if "_phoenix_type" in kwargs:
            mcs.mappings[kwargs["_phoenix_type"]] = cls
        return cls


@six.add_metaclass(PhoenixMeta)
class PhoenixObject(object):
    def __init__(self, obj):
        for key in filter(lambda x: not x.startswith("__"), dir(obj)):
            value = getattr(obj, key)
            val_type = type(value)
            if val_type in self._mappings:
                setattr(self, key, self._mappings[val_type](value))
            elif serializable(value):
                setattr(self, key, value)
            else:
                if key in ("f_locals", "f_globals"):
                    setattr(self, key, serialize_generic_obj(value))
                else:
                    setattr(self, "__tracebackhide__", True)


def _apply_over_tracebacks(method):
    def wrapper(self, *args, **kwargs):
        first_result = method(self, *args, **kwargs)
        if getattr(self, "tb_next", None) is not None:
            return getattr(self.tb_next, method.__name__)(*args, **kwargs)
        return first_result

    return wrapper


def remove_builtins(frame):
    globals_ = frame.f_globals
    valid_keys = six.viewkeys(globals_) - six.viewkeys(builtins_)
    setattr(frame, "f_globals", {key: globals_[key] for key in valid_keys})


def inject_builtins(frame):
    frame.f_globals.update(builtins_)


def inject_local_scope(frame):
    items = list(frame.f_locals.values())
    for val in (item for item in items if hasattr(item, "__globals__")):
        val.__globals__.update(frame.f_globals)


def get_traceback_files(frame, files):
    filename = os.path.abspath(frame.f_code.co_filename)
    if filename not in files:
        try:
            files[filename] = open(filename).read()
        except IOError:
            files[filename] = "couldn't locate '%s' during dump" % self.f_code.co_filename


class PhoenixTraceback(PhoenixObject):
    _phoenix_type = types.TracebackType

    def prepare_for_serialization(self):
        traceback = self
        while traceback:
            frame = traceback.tb_frame
            while frame:
                remove_builtins(frame)
                frame = frame.f_back
            traceback = traceback.tb_next

    def prepare_for_deserialization(self):
        traceback = self
        while traceback:
            frame = traceback.tb_frame
            while frame:
                inject_builtins(frame)
                inject_local_scope(frame)
                frame = frame.f_back
            traceback = traceback.tb_next

    def get_traceback_files(self):
        files = {}
        traceback = self
        while traceback:
            frame = traceback.tb_frame
            while frame:
                get_traceback_files(frame,files)
                frame = frame.f_back
            traceback = traceback.tb_next
        return files



class PhoenixFrame(PhoenixObject):
    _phoenix_type = types.FrameType

class PhoenixCode(PhoenixObject):
    _phoenix_type = types.CodeType

    def __init__(self, obj):
        super().__init__(obj)
        self.co_filename = os.path.abspath(self.co_filename)
