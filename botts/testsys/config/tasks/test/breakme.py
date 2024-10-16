import ast
import textwrap
from typing import Any

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.base.units import FnCodeUnit
from botts.testsys.components.check.checker import SequenceOf, ANYTHING, Checker, Result, Verdict
from botts.testsys.components.check.generator import ArgList
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL, Validator, REQ_RECURSION
from botts.testsys.components.extract.jupyter import FnLocator


class ShouldIncludeSpecialVar(Validator):
    def validate(self, unit: FnCodeUnit) -> str | None:
        for node in ast.walk(unit.node):
            if not isinstance(node, ast.Name):
                continue
            if node.id == 'include_me':
                return None
        return 'solution should include variable with name `include_me`'


class BreakMeChecker(Checker):
    def check(self, in_data: Any, out_data: Any, answer: Any, **kwargs) -> Result:
        student_id: int = kwargs['student_id']

        if isinstance(out_data, int):
            return Result(Verdict.IA, 'expected some other answer type but you are close')
        if not isinstance(out_data, str):
            return Result(Verdict.IA, 'completely wrong answer type')

        if len(out_data) == 0:
            return Result(Verdict.WA, 'nope, empty string is not the right answer, but it\'s not the worst guess')
        if not out_data.isalnum():
            return Result(Verdict.WA, 'some characters in your answer definitely don\'t exist in the correct answer')
        if not out_data.isnumeric():
            return Result(Verdict.WA, 'some characters in your answer are... unexpected, but overall you are closer')

        try:
            number = int(out_data)
        except ValueError:
            return Result(Verdict.WA, 'you are very close but make it a bit less fractional')

        if number < student_id:
            return Result(Verdict.WA, 'make it bigger')
        if number > student_id:
            return Result(Verdict.WA, 'make it smaller')
        return Result(Verdict.OK, None)


TASK = Task(
    id_='breakme',
    statement=Statement(
        md=textwrap.dedent('''
        `> BREAKME` \\[_Задание для проверки системы_]

        Напишите функцию `guess()`, возвращающую _какое-то_ значение неизвестного типа. 
        
        Что именно должна делать функция, не сообщается. Примеров тоже не будет. 
        Угадайте, что должна возвращать функция, по вердиктам, которые сообщаются вам после каждой 
        отправки решения на тестирование.
        
        Более того, на функцию наложено определенное ограничение. Его тоже надо угадать и выполнить, 
        ориентируясь на вердикты и сообщения о проверке.
        ''')
    ),
    include=[],
    locator=FnLocator('guess'),
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION & ShouldIncludeSpecialVar(),
    checker=BreakMeChecker(),
    tests=[
        ArgList()
    ],
    solution=None,
    extended_info=True,
)
