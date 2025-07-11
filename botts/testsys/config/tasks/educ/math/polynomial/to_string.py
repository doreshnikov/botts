import re
import textwrap
from typing import Any, Callable

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import Checker, Result, Verdict
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator
from . import *


def _to_string(p: polynomial, monomial_to_string: Callable[[float, int], str]) -> str:
    p = list(map(float, p))
    monomials = []
    for d in reversed(range(len(p))):
        if p[d] == 0:
            continue
        monomials.append(monomial_to_string(p[d], d))
    result = ' + '.join(monomials)
    return result.replace(' + -', ' - ')


def solution(p: polynomial) -> str:
    def monomial_to_string(coefficient: float, d: int) -> str:
        if d == 0:
            return f'{coefficient}'
        c_str = f'{coefficient}'
        if abs(coefficient) == 1:
            c_str = '' if coefficient == 1 else '-'
        if d == 1:
            return f'{c_str}x'
        return f'{c_str}x^{d}'

    return _to_string(p, monomial_to_string)


class StringChecker(Checker):
    def simplify(_, s: str):
        s = re.sub(r'\.0+[x$]', 'x', s)
        s = re.sub(r'\.0+$', '', s)
        return s

    def check(self, _: Any, out_data: Any, answer: str, **__) -> Result:
        if not isinstance(out_data, str):
            return Result(Verdict.IA, f"expected a string, got '{out_data}'")

        out_data = self.simplify(out_data)
        answer = self.simplify(answer)
        if out_data != answer:
            return Result(Verdict.WA, f"something isn't right in '{out_data}', expected '{answer}'")
        return Result(Verdict.OK, None)


TASK = Task(
    id_='polynomial-to-string',
    statement=Statement(
        md=textwrap.dedent('''
        `> TO STRING *`
        
        Напишите функцию `polynomial_to_string(a)`, принимающую многочлен и возвращающую его 
        строковое представление по следующим правилам:
         - мономы с коэффициентом 0 пропускаются
         - мономы чередуются через `' + '` (плюс с двумя пробелами)
         - вместо отрицательных коэффициентов стоящий перед ними плюс заменяется на минус
         - коэффициенты, равные 1 или -1, не указываются
         - мономы следуют от старшей степени к младшей
        
        Например, `polynomial_to_string([-2, -1, 1, 0, -3])` должна вернуть `-3x^4 + x^2 - x - 2`.
        ''')
    ),
    locator=FnLocator('polynomial_to_string'),
    include=[
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=StringChecker(),
    tests=[
        ArgList([0, 2, -1, 5]),
        ArgList([-5, -1.0, 1.0, 0.0, 1, 2, 3, -1.0, 1]),
        *H.repeat_test(
            ArgList(R_INT(10, 20).map(
                lambda size: R_FLOAT(-12.0, 12.0).map(
                    lambda x: -1.0 if x < -9 else (1.0 if x > 9 else (0.0 if abs(x) < 1 else x))
                ).repeat(size, as_type=list)
            )),
            number=12
        )
    ],
    solution=solution
)
