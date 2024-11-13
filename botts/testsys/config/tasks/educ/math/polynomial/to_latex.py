import re
import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.process.check import Checker
from botts.testsys.components.process.validate import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *
from .to_string import StringChecker as _Checker_to_string
from .to_string import TASK as _TASK_to_string
from .to_string import _to_string


def solution(p: polynomial) -> str:
    def monomial_to_string(coefficient: float, d: int) -> str:
        if d == 0:
            return f'{coefficient}'
        c_str = f'{coefficient}'
        if abs(coefficient) == 1:
            c_str = '' if coefficient == 1 else '-'
        if d == 1:
            return f'{c_str}x'
        return f'{c_str}x^{{{d}}}'

    return _to_string(p, monomial_to_string)


class LatexChecker(_Checker_to_string):
    def simplify(_, s: str):
        s = re.sub(r'\^\{1}', r'^1', s)
        s = re.sub(r'\{(\d)}', r'\g<1>', s)
        s = re.sub(r'\.0+x', 'x', s)
        s = re.sub(r'\.0+\$', '$', s)
        s = re.sub(r'\s', '', s)
        return s


TASK = Task(
    id_='polynomial-to-latex',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        <<Перенести условие из блокнота>>
        ''')
    ),
    locator=FnLocator('polynomial_to_latex'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=LatexChecker(),
    tests=_TASK_to_string.tests,
    solution=solution
)
