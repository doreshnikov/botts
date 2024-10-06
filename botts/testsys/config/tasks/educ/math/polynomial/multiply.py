import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, SINGLE_FLOAT_6
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *
from .add import TASK as _TASK_add


def solution(p: polynomial, q: polynomial) -> polynomial:
    r = [0.0 for _ in range(len(p) + len(q) - 1)]
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            r[i + j] += p[i] * q[j]
    return r


TASK = Task(
    id_='polynomial-multiply',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        <<Добавить адекватное условие (+примеры из блокнота)>>
        ''')
    ),
    locator=FnLocator('polynomial_multiply'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(SINGLE_FLOAT_6),
    tests=_TASK_add.tests,
    solution=solution,
    time_limit=3
),
