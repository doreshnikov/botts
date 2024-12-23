import textwrap
import math

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import SINGLE_NUMBER, VERBOSE
from botts.testsys.components.check.generator import ArgList
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator


def solution_2024(n: int):
    return math.floor(math.sqrt(2 * n) + 0.5)


def solution_2025(n: int):
    a = [220, 1184, 2620, 5020, 6232, 10744, 12285, 17296, 63020, 
         66928, 67095, 69615, 79750, 100485, 122265, 122368, 141664, 
         142310, 171856, 176272, 185368, 196724, 280540, 308620, 319550, 
         356408, 437456, 469028, 503056, 522405, 600392, 609928]
    return a[n - 1]


TASK = Task(
    id_='sequence-element',
    statement=Statement(
        md=textwrap.dedent('''
        `> NEW YEAR SEQUENCE`
        
        Напишите функцию `sequence_element(n)`, вычисляющую `n`-й элемент 
        **новогодней** последовательности.
        
        **Подсказка**: `oeis.org` в помощь. Ориентируйтесь на сообщения чекера, 
        чтобы понять, чему равны первые элементы последовательности. Следующие 
        как-нибудь найдутся.
        
        Также в этой задаче для вас уже заимпорчен модуль `math`, но в зависимости 
        от текущего года он может оказаться не особо полезен.
        ''')
    ),
    locator=FnLocator('sequence_element'),
    include=[
        inc('import math')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=VERBOSE(SINGLE_NUMBER),
    tests=[
        ArgList(i) for i in range(1, 31)
    ],
    solution=solution_2025
)