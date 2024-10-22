import math
import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SINGLE_FLOAT_6
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *


def solution(alpha: float, v: float):
    return (v * math.sin(math.radians(alpha))) ** 2 / 2 / g


TASK = Task(
    id_='highest-point',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        `> HIGHEST POINT`
        
        Есть снаряд, вылетающий из точки с координатами `(0, 0)` под углом `alpha` градусов к земной поверхности 
        со скоростью `v` м/с. Силой сопротивления воздуха можно пренебречь, одна единица расстояния на координатной 
        плоскости равна одному метру.

        Функция `highest_point(alpha, v)` должна возвращать самое высокое его положение в воздухе 
        (максимальную y-координату). Модуль `math` уже импортирован, также вы можете использовать в решении 
        переменную `g`, в нее автоматически будет подставлено значения 9.81.
        ''')
    ),
    locator=FnLocator('highest_point'),
    include=[
        inc('import math'),
        inc('g = 9.81')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SINGLE_FLOAT_6,
    tests=[
        ArgList(12.0, 45.0, 10.0),
        ArgList(10.0, 90.0, 10.0),
        *H.repeat_test(
            ArgList(R_FLOAT(0.1, 100.0), R_FLOAT(0.1, 179.9), R_FLOAT(0.1, 100.0)),
            number=13
        )
    ],
    solution=solution
)
