import textwrap

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SequenceOf, ANYTHING
from botts.testsys.components.check.generator import ArgList
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from resources.tests.python.x import X


def solution(a: list) -> list:
    b = []
    for i, item in enumerate(a):
        found = False
        for prev_item in b:
            if item == prev_item:
                found = True
                break
        if not found:
            b.append(item)
    return b


TASK = Task(
    id_='unique',
    statement=Statement(
        md=textwrap.dedent('''
        `> UNIQUE` \\[_Задание для проверки системы_]
        
        Напишите функцию `unique(a)`, принимающую один аргумент \N{EN DASH} 
        массив из произвольных элементов, и возвращающую массив из тех 
        же элементов в том же порядке, но с удаленными повторениями.
        
        *Пример*:
        - `unique([1, 2, 3, 1, 4, 2, 0])` должна вернуть `[1, 2, 3, 4, 0]`
        - `unique([[], [1, 2], [], [1], 'x', [1, 2]])` должна вернуть `[[], [1, 2], [1], 'x']`
        ''')
    ),
    include=[
        inc(f'from {X.__module__} import X')
    ],
    locator=FnLocator('unique'),
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=SequenceOf(ANYTHING),
    tests=[
        ArgList([1, 2, 3, 1, 4, 2, 0]),
        ArgList([[], [1, 2], [], [1], 'x', [1, 2]]),
        ArgList([]),
        ArgList(['x', 'y', 'z', 1, 2, 3]),
        ArgList([1, 1, 1]),
        ArgList([{}, set(), [], X()]),
        ArgList([X(), X(), X, X(), X, X])
    ],
    solution=solution,
)
