from typing import Callable

Executor = Callable[[Callable], Callable]


def _substitute_stdout(fn):
    import contextlib
    import io

    def wrapped(*args, **kwargs):
        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            fn(*args, **kwargs)
            return buffer.getvalue()

    return wrapped


SUBSTITUTE_STDOUT: Executor = _substitute_stdout
