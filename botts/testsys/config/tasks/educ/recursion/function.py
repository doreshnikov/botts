import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SINGLE_NUMBER
from botts.testsys.components.check.generator import ArgList, H, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *


def solution(n: int, m: int) -> int:
    if n == 0:
        return m + 1
    if m == 0:
        return solution(n - 1, 1)
    return solution(n - 1, solution(n, m - 1))


TASK = Task(
    id_='ackermann',
    statement=Statement(
        md=textwrap.dedent('''
        `> FUNCTION`
        
        Напишите реализацию вычисления [функции Аккермана](https://ru.wikipedia.org/wiki/Функция_Аккермана)
        в определении Петер (от двух целочисленных параметров `n` и `m`).
        
        Функция должна называться `ackermann`.
        ''')
    ),
    locator=FnLocator('ackermann'),
    include=[
        inc('from sys import setrecursionlimit'),
        inc('setrecursionlimit(100000)')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SINGLE_NUMBER,
    tests=[
        ArgList(0, 0),
        ArgList(0, 1),
        ArgList(0, 2),
        ArgList(0, 3),
        ArgList(0, 4),
        ArgList(0, 5),
        ArgList(1, 0),
        ArgList(2, 0),
        ArgList(3, 0),
        ArgList(4, 0),
        *H.repeat_test(
            R_INT(1, 3).map(
                lambda n: R_INT(1, 10).map(
                    lambda m: ArgList(n, m)
                )
            ),
            number=15
        )
    ],
    solution=solution,
    time_limit=10
)
