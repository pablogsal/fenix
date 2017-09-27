import collections
import sys

import pytest
import dill as pickle

from fenix import dump_management

@pytest.fixture
def prepare_function():
    code = ("import sys\n"
            "def test_func(input):\n    local_var=input"
            "\n    try:\n        1/0\n    except ZeroDivisionError as e:"
            "\n        ex_type, ex, tb = sys.exc_info()"
            "\n        return tb")
    local_dict = {}
    exec(compile(code, __file__, "exec"), local_dict)
    return local_dict["test_func"]


def test_serialization(prepare_function):
    # GIVEN
    local_var = [1, -1, 2.3,
                 "Hello", ("a", "b", 1), collections.defaultdict(a=1),
                 {"test": "Test"}]
    test_func = prepare_function

    # WHEN

    traceback = (test_func(local_var))
    dump = dump_management.prepare_dump(traceback)
    dump["traceback"].tb_frame.f_back = None

    # THEN

    serial_version = pickle.dumps(dump)
    unserial_version = pickle.loads(serial_version)
    new_traceback = unserial_version["traceback"]
    new_traceback.prepare_for_deserialization()

    frame = new_traceback.tb_frame
    assert "local_var" in frame.f_locals
    assert frame.f_locals["local_var"] == local_var


def test_serialization_of_unpickable_obj(prepare_function):
    # GIVEN
    class UnPickable:
        def __init__(self):
            self.a = "Hello"

        def __reduce_ex__(self, p):
            raise pickle.PicklingError

        def __str__(self):
            return "UnPickable"

        __repr__ = __str__

    local_var = UnPickable()
    test_func = prepare_function

    # WHEN

    traceback = (test_func(local_var))
    dump = dump_management.prepare_dump(traceback)
    dump["traceback"].tb_frame.f_back = None

    # THEN

    serial_version = pickle.dumps(dump)
    unserial_version = pickle.loads(serial_version)
    new_traceback = unserial_version["traceback"]
    new_traceback.prepare_for_deserialization()

    frame = new_traceback.tb_frame
    assert "local_var" in frame.f_locals
    assert isinstance(frame.f_locals["local_var"], str)
    assert frame.f_locals["local_var"] == "UnPickable"


def test_serialization_of_unpickable_obj_in_container(prepare_function):
    # GIVEN
    class UnPickable:
        def __init__(self):
            self.a = "Hello"

        def __reduce_ex__(self, p):
            raise pickle.PicklingError

        def __str__(self):
            return "UnPickable"

        __repr__ = __str__

    local_var = [[1, UnPickable()],
                 (1, UnPickable()),
                 collections.OrderedDict(a=1, b=UnPickable())]
    test_func = prepare_function

    # WHEN

    traceback = (test_func(local_var))
    dump = dump_management.prepare_dump(traceback)
    dump["traceback"].tb_frame.f_back = None

    # THEN

    serial_version = pickle.dumps(dump)
    unserial_version = pickle.loads(serial_version)
    new_traceback = unserial_version["traceback"]
    new_traceback.prepare_for_deserialization()

    frame = new_traceback.tb_frame
    assert "local_var" in frame.f_locals
    actual_local_var = frame.f_locals["local_var"]
    assert actual_local_var == [[1, "UnPickable"],
                                "(1, UnPickable)",
                                collections.OrderedDict(a=1, b="UnPickable")]
