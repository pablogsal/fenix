import pytest

from fenix import dump_management
import dill as pickle

@pytest.fixture
def prepare_function():
    code = ("def test_func(input):\n    local_var=input"
            "\n    try:\n        1/0\n    except ZeroDivisionError as e:"
            "\n        return e")
    local_dict = {}
    exec(compile(code, __file__, "exec"), local_dict)
    return local_dict["test_func"]


@pytest.mark.parametrize("local_var",[1,-1,(1,-1),[1,-1],{1:2}])
def test_serialization(local_var,prepare_function):
    # GIVEN

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
