import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, SINGLE_FLOAT_6
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *


def solution(p: polynomial) -> polynomial:
    r = [p[i] * i for i in range(len(p))]
    if len(r) == 1:
        return [0]
    return r[1:]


TASK = Task(
    id_='polynomial-derivative',
    statement=Statement(
        md=textwrap.dedent('''
        `> DERIVATIVE`
        
        Напишите функцию `polynomial_derivative(a)`, вычисляющую производную многочлена.
        Например, `polynomial_derivative([1, 2, 3])` должна вернуть `[2, 6]`.
        ''')
    ),
    locator=FnLocator('polynomial_derivative'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(SINGLE_FLOAT_6),
    tests=[
        ArgList([0, 2, -1, 5]),
        ArgList([-5, -1, 1, 0, 1, 2, 3, -1, 1]),
        ArgList([1]),
        *H.repeat_test(
            ArgList(R_INT(10, 30).map(lambda size: R_FLOAT(-100.0, 100.0).repeat(size, as_type=list))),
            number=12
        )
    ],
    solution=solution
)
