import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, SINGLE_FLOAT_6
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *
from .divide import TASK as _TASK_divide


def solution(p: polynomial, q: polynomial) -> polynomial:
    r = [0.0 for _ in range(len(p) + len(q) - 1)]
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            r[i + j] += pi * qj
    return r


TASK = Task(
    id_='polynomial-multiply',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        `> MULTIPLY`
        
        Напишите функцию `polynomial_multiply(a, b)`, вычисляющую произведение двух многочленов.
        Например, `polynomial_multiply([1, 3, 2], [1, 1])` должна вернуть `[1, 4, 5, 2]`.
        ''')
    ),
    locator=FnLocator('polynomial_multiply'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(SINGLE_FLOAT_6),
    tests=_TASK_divide.tests,
    solution=solution,
    time_limit=3
)
