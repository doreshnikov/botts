import math
import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.process.check import SINGLE_FLOAT_4
from botts.testsys.components.process.generate import ArgList, H, R_FLOAT
from botts.testsys.components.process.validate import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *


def solution(a: point, b: point, c: point):
    v1x, v1y = a[0] - b[0], a[1] - b[1]
    v2x, v2y = c[0] - b[0], c[1] - b[1]
    y = v1x * v2y - v2x * v1y
    x = v1x * v2x + v1y * v2y
    return abs(math.degrees(math.atan2(y, x)))


TASK = Task(
    id_='angle',
    statement=Statement(
        md=textwrap.dedent('''
        `> ANGLE`
        
        Напишите функцию `angle(a, b, c)`, принимающую координаты трех точек на плоскости 
        (как `tuple[float, float]`) и возвращающую величину угла на этих трех точках (с вершиной 
        во второй из них, то есть угла `abc`).
        
        Ответ требуется вывести в *градусах* от 0 до 360. Модуль `math` уже импортирован.
        ''')
    ),
    locator=FnLocator('angle'),
    include=[
        inc('import math'),
        inc('point = tuple[float, float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SINGLE_FLOAT_4,
    tests=[
        ArgList((0.0, 0.0), (3.3, 0.0), (0.0, 3.3)),
        ArgList((-2.0, -2.0), (0.0, 0.0), (5.0, 5.0)),
        ArgList((-2.0, 2.0), (0.0, 0.0), (4.0, -4.0)),
        *H.repeat_test(
            ArgList(R_POINT, R_POINT, R_POINT).retry_until(H.distinct),
            7
        )
    ],
    solution=solution
)
