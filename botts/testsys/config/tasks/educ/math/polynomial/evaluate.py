import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SINGLE_FLOAT_4
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *
from .multiply import solution as polynomial_multiply


def solution(p: polynomial, x: float) -> float:
    return sum(pi * x ** i for i, pi in enumerate(p))


TASK = Task(
    id_='polynomial-evaluate',
    statement=Statement(
        md=textwrap.dedent('''
        `> EVALUATE`
        
        Напишите функцию `polynomial_evaluate(a, x)`, принимающую многочлен и число, и 
        возвращающую результат вычисления многочлена `a` в заданном `x`.
        Например, `polynomial_evaluate([1, 2, -1], 0.5)` должна вернуть `1.75`.
        ''')
    ),
    locator=FnLocator('polynomial_evaluate'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SINGLE_FLOAT_4,
    tests=[
        ArgList([3, 0, 2], 1),
        ArgList([1] + [0 for _ in range(10)], 12),
        ArgList([100.5, -10.5, 12.5, 33.1], 77),
        ArgList([1, 2, 3, 4], 0.4),
        *H.repeat_test(
            ArgList(
                R_FLOAT(-100.0, 100.0).repeat(10, as_type=list),
                R_FLOAT(-10.0, 10.0)
            ),
            number=4
        ),
        *H.repeat_test(
            R_INT(5, 10).map(
                lambda size: R_FLOAT(-5.0, 5.0).repeat(size, as_type=list).map(
                    lambda it: R_FLOAT(-10.0, 10.0).map(
                        lambda x: ArgList(polynomial_multiply(it, [-x, 1]), x)
                    )
                )
            ),
            number=10
        )
    ],
    solution=solution
)
