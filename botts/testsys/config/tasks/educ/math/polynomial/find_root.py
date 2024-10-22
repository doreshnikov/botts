import numbers
import textwrap
from typing import Any

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import Checker, Result, Verdict
from botts.testsys.components.check.generator import ArgList, H, R_FLOAT, R_INT, Arguments
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator

from . import *
from .multiply import solution as polynomial_multiply


class FindRootChecker(Checker):
    def check(self, in_data: Arguments, out_data: Any, _: Any, **__) -> Result:
        if not isinstance(out_data, numbers.Number):
            return Result(Verdict.IA, f"expected a number, got '{out_data}'")

        # noinspection PyTypeChecker
        value = polynomial_calculate(*in_data.args, out_data)
        if abs(value) > 0.0001:
            return Result(Verdict.WA, f"{out_data} is not a root: f(x) = {value}")
        return Result(Verdict.OK, None)


TASK = Task(
    id_='polynomial-find-root',
    statement=Statement(
        # TODO
        md=textwrap.dedent('''
        <<Перенести условие из блокнота>>
        ''')
    ),
    locator=FnLocator('polynomial_find_root'),
    include=[
        inc('import math'),
        inc('polynomial = list[int | float]')
    ],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=FindRootChecker(),
    tests=[
        ArgList([1, 2, 1]),
        ArgList([-10, 1]),
        *H.repeat_test(
            R_INT(5, 10).map(
                lambda size: R_FLOAT(-10.0, 10.0).repeat(size, as_type=list).map(
                    lambda it: R_FLOAT(-100.0, 100.0).map(
                        lambda x: ArgList(polynomial_multiply(it, [-x, 1]))
                    )
                )
            ),
            number=13
        )
    ],
    solution=None
)
