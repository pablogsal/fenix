import types
import os
import six
import dill as pickle

try:
    import builtins

    builtins_ = builtins.__dict__
except ImportError:
    builtins_ = __builtins__


def serializable(obj):
    try:
        pickle.dumps(obj)
    except:
        return False
    else:
        return True


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
        self.d_class = str(obj.__class__.__name__)
        for key in filter(lambda x: not x.startswith("__"), dir(obj)):
            value = getattr(obj, key)
            if serializable(value):
                setattr(self, key, value)
            else:
                val_type = type(value)
                if val_type in self._mappings:
                    setattr(self, key, self._mappings[val_type](value))
                elif key in ("f_locals", "f_globals"):
                    setattr(self, key, {k: val if serializable(val)
                            else str(val) for k, val in value.items()})
                else:
                    setattr(self, "__tracebackhide__", True)


def _apply_over_tracebacks(method):
    def wrapper(self, *args, **kwargs):
        first_result = method(self, *args, **kwargs)
        if getattr(self, "tb_next", None) is not None:
            return getattr(self.tb_next, method.__name__)(*args, **kwargs)
        return first_result

    return wrapper


class PhoenixTraceback(PhoenixObject):
    _phoenix_type = types.TracebackType

    @_apply_over_tracebacks
    def remove_builtins(self):
        self.tb_frame.remove_builtins()

    @_apply_over_tracebacks
    def inject_builtins(self):
        self.tb_frame.inject_builtins()

    @_apply_over_tracebacks
    def inject_local_scope(self):
        self.tb_frame.inject_local_scope()

    @_apply_over_tracebacks
    def get_traceback_files(self, files=None):
        if files is None:
            files = {}
        self.tb_frame.get_traceback_files(files)
        return files


def _apply_over_frames(method):
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        if getattr(self, "f_back", None) is not None:
            return getattr(self.f_back, method.__name__)(*args, **kwargs)

    return wrapper


class PhoenixFrame(PhoenixObject):
    _phoenix_type = types.FrameType

    @_apply_over_frames
    def remove_builtins(self):
        globals_ = self.f_globals
        valid_keys = globals_.keys() - builtins_.keys()
        setattr(self, "f_globals", {key: globals_[key] for key in valid_keys})

    @_apply_over_frames
    def inject_builtins(self):
        self.f_globals.update(builtins_)

    @_apply_over_frames
    def inject_local_scope(self):
        items = list(self.f_locals.values())
        for val in (item for item in items if hasattr(item, "__globals__")):
            val.__globals__.update(self.f_globals)

    @_apply_over_frames
    def get_traceback_files(self, files):
        filename = os.path.abspath(self.f_code.co_filename)
        if filename not in files:
            try:
                files[filename] = open(filename).read()
            except IOError:
                files[filename] = "couldn't locate '%s' during dump" % self.f_code.co_filename
