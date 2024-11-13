import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.process.check import SINGLE_FLOAT_6
from botts.testsys.components.process.generate import ArgList, H
from botts.testsys.components.process.validate import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator
from . import *


def solution(a: point, b: point, c: point):
    v1x, v1y = b[0] - a[0], b[1] - a[1]
    v2x, v2y = c[0] - a[0], c[1] - a[1]
    value = (v1x * v2y - v2x * v1y) / 2
    return abs(value)


TASK = Task(
    id_='triangle-area',
    statement=Statement(
        md=textwrap.dedent('''
        `> TRIANGLE AREA`
        
        Напишите функцию `triangle_area`, принимающую три точки (точка \N{EN DASH} `tuple` из двух
         `float`), и возвращающую площадь треугольника с вершинами в данных точках.
        
        *Примечание*: формула Герона не даст достаточной точности, почитайте про другие способы 
        определить площадь треугольника по координатам его вершин.  Модуль `math` уже импортирован.
        ''')
    ),
    locator=FnLocator('triangle_area'),
    include=[
        inc('import math'),
        inc('point = tuple[float, float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SINGLE_FLOAT_6,
    tests=[
        ArgList((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)),
        ArgList((0.0, 0.0), (5.0, 5.0), (10.0, 10.0)),
        *H.repeat_test(
            ArgList(R_POINT, R_POINT, R_POINT),
            8
        )
    ],
    solution=solution
)
