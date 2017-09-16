import collections

import dill as pickle


def serialize_generic_obj(item):
    if isinstance(item, str):
        pass
    elif isinstance(item, collections.Mapping):
        keys = item.keys()
        vals = item.values()
        for k, v in zip(keys, vals):
            if not serializable(k):
                k = serialize_generic_obj(k)
                del item[k]
            if not serializable(v):
                v = serialize_generic_obj(v)
            item[k] = v
    elif isinstance(item, collections.Sequence):
        for index, elem in enumerate(item):
            if not serializable(elem):
                item[index] = serialize_generic_obj(elem)
    else:
        item = str(item)
    return item


def serializable(obj):
    try:
        pickle.dumps(obj)
    except Exception:
        return False
    else:
        return True