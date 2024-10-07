import numbers
import re
from datetime import datetime
from typing import Any

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task
from botts.testsys.components.check.checker import Checker, SequenceOf, Result, SINGLE_FLOAT_6, SINGLE_STRING, \
    Verdict
from botts.testsys.components.check.generator import ArgList, Arguments, H, R_INT, R_FLOAT
from botts.testsys.components.check.validator import NO_EVAL, NO_EXEC, NO_IMPORTS, NO_RECURSION, REQ_RECURSION
from botts.testsys.components.extract.jupyter import FnLocator
from botts.testsys.components.test.event import Event




def recurrent_f(x):
    return x if x < 2 else 2 * recurrent_f(x ** 0.5) + 2 * x - 1


def solve_hanoi(i, j, n):
    if n == 1:
        return [f'{i} -> {j}']

    k = 3 - i - j
    actions = []
    actions += solve_hanoi(i, k, n - 1)
    actions.append(f'{i} -> {j}')
    actions += solve_hanoi(k, j, n - 1)
    return actions


def approximation(a, k, n):
    x = 1.0
    for i in range(n):
        x = ((k - 1) * x + a / (x ** (k - 1))) / k
    return x


HW02 = Event(
    'Homework 02',
    datetime(year=2023, month=11, day=5, hour=0, minute=0, second=0),
    [


        Task(
            id_='3-1-recurrent',
            locator=FnLocator('f'),
            include=[
                inc('import math')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(1),
                ArgList(2),
                ArgList(144),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.0, 1e5)),
                    number=6
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(1e8, 1e9)),
                    number=6
                )
            ],
            solution=recurrent_f
        ),
        Task(
            id_='3-2-hanoi',
            locator=FnLocator('solve_hanoi'),
            include=[],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION,
            checker=SequenceOf(SINGLE_STRING),
            tests=[
                ArgList(0, 2, 4),
                *H.repeat_test(
                    R_INT(0, 2).repeat(2).retry_until(H.distinct).map(
                        lambda ij: R_INT(1, 12).map(
                            lambda n: ArgList(ij[0], ij[1], n)
                        )
                    ),
                    number=20
                )
            ],
            solution=solve_hanoi
        ),
        Task(
            id_='3-3-1-rec-approximation',
            locator=FnLocator('recursive_approximation'),
            include=[
                inc('from sys import setrecursionlimit\n'
                    'setrecursionlimit(100000)')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(10.0, 178324.0, 10000),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1.0, 1e5), 2),
                    number=7
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1e5, 1e9), 10000),
                    number=7
                )
            ],
            solution=approximation
        ),
        Task(
            id_='3-3-2-iter-approximation',
            locator=FnLocator('iterative_approximation'),
            include=[],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & NO_RECURSION,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(10.0, 178324.0, 10000),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1.0, 1e5), 2),
                    number=7
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1e5, 1e9), 10000),
                    number=7
                )
            ],
            solution=approximation
        )
    ]
)
