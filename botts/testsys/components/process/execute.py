import ast
import inspect

from abc import ABC, abstractmethod
from typing import Callable

from ..base.code import CodeUnit


class Executor(ABC):
    @abstractmethod
    def wrap_callable(fn: Callable) -> Callable:
        pass
    
    @abstractmethod
    def wrap_source(source: CodeUnit) -> CodeUnit:
        pass
    

class DecoratorExecutor(Executor):
    def __init__(self, wrapper: Callable[[Callable], Callable]):
        self.wrapper = wrapper
        self.name = wrapper.__name__
        self.source = inspect.getsource(wrapper)
        
    def wrap_callable(self, fn: Callable) -> Callable:
        return self.wrapper(fn)
    
    def wrap_source(self, source: CodeUnit):
        wrapped_source = self.source + '\n\n' + f'@{self.name}\n{source.source}',
        return CodeUnit(
            wrapped_source,
            ast.parse(wrapped_source)
        )


def _substitute_stdout(fn):
    import contextlib
    import io

    def wrapped(*args, **kwargs):
        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            fn(*args, **kwargs)
            return buffer.getvalue()

    return wrapped


SUBSTITUTE_STDOUT = DecoratorExecutor(_substitute_stdout)
