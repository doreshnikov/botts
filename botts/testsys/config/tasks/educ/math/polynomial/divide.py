import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, SINGLE_FLOAT_6
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *


def solution(p: polynomial, q: polynomial) -> tuple[polynomial, polynomial]:
    quot = []
    while len(q) > 0 and q[-1] == 0:
        q.pop()
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    while len(p) >= len(q):
        divv = p[-1] / q[-1]
        for i in range(len(q)):
            p[-i - 1] -= q[-i - 1] * divv
        p.pop()
        quot.append(divv)

    quot.reverse()
    while len(p) > 0 and p[-1] == 0:
        p.pop()
    if len(p) == 0:
        p.append(0)
    return quot, p


TASK = Task(
    id_='polynomial-divide',
    statement=Statement(
        md=textwrap.dedent('''
        `> DIVIDE *`
        
        Напишите функцию `polynomial_divide(a, b)`, вычисляющую частное двух многочленов.
        Многочлены делятся в столбик, необходимо вернуть пару из неполного частного и остатка.
        Например, `polynomial_divide([1, 3, 1], [1, 1])` должна вернуть `[2, 1], [-1]`.
        ''')
    ),
    locator=FnLocator('polynomial_divide'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(SequenceOf(SINGLE_FLOAT_6), as_type=tuple),
    tests=[
        ArgList([2, 1, 3, 2], [6, 0, 3]),
        ArgList([100.5, -10.5, 12.5, 33.1], [-100, 10, -12]),
        ArgList([1, 2, 3, 4], [-1, -2, -3, -4]),
        ArgList([1], [1]),
        *H.repeat_test(
            ArgList(
                R_FLOAT(-100.0, 100.0).repeat(30, as_type=list).map(lambda t: t + [1.0]),
                R_FLOAT(-100.0, 100.0).repeat(20, as_type=list).map(lambda t: t + [1.0])
            ),
            number=11
        )
    ],
    solution=solution,
    time_limit=3
)
