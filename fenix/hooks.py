import functools
from fenix.dump_management import save_dump


class Fenix(object):
    """
    This class can be used both as a context manager and a decorator. it will assure
    that if any exception is being raised inside the protected code region, a fenix
    core dump will be produced in the path specified by filepath.

    :param: filepath: The file path to store the fenix core dump

    Example of usage

    It can be used as a decorator:

    >>> @Fenix("./fenix.dump")
    ... def mydangerousfunction():
    ...     pass

    or a context manager

    >>> with Fenix("./fenix.dump"):
    ...     mydangerousfunction()


    """

    def __init__(self, filepath):
        self.filepath = filepath

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_dump(self.filepath, exc_tb)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper
