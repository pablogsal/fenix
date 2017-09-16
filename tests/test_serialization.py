import pytest

from fenix import dump_management
import dill as pickle
import collections


@pytest.fixture
def prepare_function():
    code = ("def test_func(input):\n    local_var=input"
            "\n    try:\n        1/0\n    except ZeroDivisionError as e:"
            "\n        return e")
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

    traceback = test_func(local_var).__traceback__
    dump = dump_management.prepare_dump(traceback)
    dump["traceback"].tb_frame.f_back = None

    # THEN

    serial_version = pickle.dumps(dump)
    unserial_version = pickle.loads(serial_version)
    new_traceback = unserial_version["traceback"]

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

    local_var = UnPickable()
    test_func = prepare_function

    # WHEN

    traceback = test_func(local_var).__traceback__
    dump = dump_management.prepare_dump(traceback)
    dump["traceback"].tb_frame.f_back = None

    # THEN

    serial_version = pickle.dumps(dump)
    unserial_version = pickle.loads(serial_version)
    new_traceback = unserial_version["traceback"]

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

    local_var = [[1, UnPickable()],
                 collections.OrderedDict(a=1, b=UnPickable())]
    test_func = prepare_function

    # WHEN

    traceback = test_func(local_var).__traceback__
    dump = dump_management.prepare_dump(traceback)
    dump["traceback"].tb_frame.f_back = None

    # THEN

    serial_version = pickle.dumps(dump)
    unserial_version = pickle.loads(serial_version)
    new_traceback = unserial_version["traceback"]

    frame = new_traceback.tb_frame
    assert "local_var" in frame.f_locals
    actual_local_var = frame.f_locals["local_var"]
    assert actual_local_var[0] == [1, "UnPickable"]
    assert actual_local_var[1] == collections.OrderedDict(a=1, b="UnPickable")
