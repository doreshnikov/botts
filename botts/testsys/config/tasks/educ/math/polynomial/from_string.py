import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, SINGLE_FLOAT_6
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *
from .to_string import solution as polynomial_to_string


def solution(s: str) -> polynomial:
    items = ['+']
    if s.startswith('-'):
        items[0] = '-'
        s = s[1:]
    items += s.split()

    p = [0 for _ in range(len(items) // 2)]
    for sign, monomial in zip(items[::2], items[1::2]):
        sign = 1 if sign == '+' else -1
        value = monomial.split('^')
        d = int(value[1]) if len(value) > 1 else (1 if 'x' in value[0] else 0)
        coefficient = value[0][:value[0].find('x')]
        if coefficient == '':
            coefficient = '1'

        while d >= len(p):
            p.append(0)
        # noinspection PyTypeChecker
        p[d] = float(coefficient) * sign

    return p


TASK = Task(
    id_='polynomial-from-string',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        <<Перенести условие из блокнота>>
        ''')
    ),
    locator=FnLocator('polynomial_from_string'),
    include=[
        inc('polynomial = list[float | int]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(SINGLE_FLOAT_6),
    tests=[
        ArgList('1'),
        ArgList('-x^4'),
        ArgList('2x^3'),
        ArgList('-x^5 + 4x^3 - x + 7.0'),
        ArgList('-x^5 + 4x^3'),
        ArgList(polynomial_to_string([-5, -1.0, 1.0, 0.0, 1, 2, 3, -1.0, 1])),
        *H.repeat_test(
            ArgList(R_INT(10, 20).map(
                lambda size: R_FLOAT(-12.0, 12.0).map(
                    lambda x: -1.0 if x < -9 else (1.0 if x > 9 else (0.0 if abs(x) < 1 else x))
                ).repeat(size, as_type=list).map(
                    lambda it: polynomial_to_string(it if it[-1] != 0 else it + [1])
                )
            )),
            number=14
        )
    ],
    solution=solution
),
