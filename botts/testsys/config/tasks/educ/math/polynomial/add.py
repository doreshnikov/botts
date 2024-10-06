import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, SINGLE_FLOAT_6
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *


def solution(p: polynomial, q: polynomial) -> polynomial:
    r = [0.0 for _ in range(max(len(p), len(q)))]
    for i, pi in enumerate(p):
        r[i] += pi
    for i, qi in enumerate(q):
        r[i] += qi
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


TASK = Task(
    id_='polynomial-add',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        <<Перенести условие из блокнота>>
        ''')
    ),
    locator=FnLocator('polynomial_add'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(SINGLE_FLOAT_6),
    tests=[
        ArgList([3, 0, 2], [-1, 0, -2]),
        ArgList([1] + [0 for _ in range(10)], [1, -1] + [0 for _ in range(9)]),
        ArgList([100.5, -10.5, 12.5, 33.1], [-100, 10, -12]),
        ArgList([1, 2, 3, 4], [-1, -2, -3, -4]),
        *H.repeat_test(
            ArgList(
                R_FLOAT(-100.0, 100.0).repeat(20, as_type=list),
                R_FLOAT(-100.0, 100.0).repeat(30, as_type=list)
            ),
            number=4
        ),
        *H.repeat_test(
            R_INT(30, 50).map(
                lambda tail: R_INT(0, 5).map(
                    lambda size: R_FLOAT(-100.0, 100.0).repeat(tail, as_type=list).map(
                        lambda t: ArgList(
                            R_FLOAT(-100.0, 100.0).repeat(size, as_type=list).map(
                                lambda it: it + t
                            ),
                            R_FLOAT(-100.0, 100.0).repeat(size, as_type=list).map(
                                lambda it: it + [-x for x in t]
                            )
                        )
                    )
                )
            ),
            number=12
        )
    ],
    solution=solution
),
