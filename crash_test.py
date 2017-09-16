import pickle

import numpy as np
import collections

from fenix import dump_management

bbb = 1


def crash(type, value, traceback):
    filename = __file__ + '.dump'
    print("Exception caught, writing %s" % filename)
    serializers.save_dump(filename, traceback=traceback)
    print("Run 'pydump %s' to debug" % (filename))


# sys.excepthook = crash
def chel():
    return 34


class A:
    def __init__(self):
        self.a = "Hello"

    def __reduce_ex__(self, p):
        raise pickle.PicklingError


def foo():
    foovar = A()
    return bar()


def bar():
    barvar = "hello"
    lel = np.arange(100)
    list_sample = [1, 2, 3, 4,A()]
    s = collections.OrderedDict(s=4,stuff=A())
    dict_sample = {'a': 1, 'b': 2}
    return baz()


def baz():
    global bbb
    momo = Momo()
    if bbb > 0:
        momo.raiser()
    else:
        return 5


class Momo(object):
    def __init__(self):
        self.momodata = "Some data"

    def raiser(self):
        raise Exception("BOOM!")


def main():
    foo()



if __name__ == '__main__':
    main()
