import math
import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SINGLE_FLOAT_6
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator


def solution(x: float, mu: float, sigma: float):
    return 0.5 * (1 + math.erf((x - mu) / sigma / math.sqrt(2)))


TASK = Task(
    id_='normal-cdf',
    statement=Statement(
        md=textwrap.dedent('''
        Для данных параметров $x$, $\\mu$ и $\\sigma$ посчитайте значение 
        функции распределения (CDF) нормального распределения с такими параметрами.  
        ''')
    ),
    locator=FnLocator('normal_cdf'),
    include=[
        inc('import math')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SINGLE_FLOAT_6,
    tests=[
        ArgList(42.0, 42.0, 13.0),
        ArgList(32.0, 42.0, 13.0),
        *H.repeat_test(
            ArgList(R_FLOAT(-10.0, 10.0), R_FLOAT(-10.0, 10.0), R_FLOAT(0.1, 4.0)),
            4
        ),
        *H.repeat_test(
            ArgList(R_FLOAT(-100.0, 100.0), R_FLOAT(-10.0, 10.0), R_FLOAT(0.1, 10.0)),
            4
        )
    ],
    solution=solution
),
