import textwrap
from typing import Any

from botts.db.dao.students import Students
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.process.check import Checker, Result, Verdict
from botts.testsys.components.process.execute import SUBSTITUTE_STDOUT
from botts.testsys.components.process.generate import ArgList
from botts.testsys.components.process.validate import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator


class WhoamiChecker(Checker):
    def check(self, in_data: Any, out_data: Any, answer: Any, **kwargs) -> Result:
        student_id: int = kwargs['student_id']
        student = Students.get_student_by_id(student_id)

        if not isinstance(out_data, str):
            return Result(Verdict.IA, f"result '{out_data}' is not a string")
        out_data = out_data.strip()
        if out_data != student.name:
            return Result(Verdict.WA, f"result '{out_data}' is not your name")

        return Result(Verdict.OK, None)


TASK = Task(
    id_='whoami',
    statement=Statement(
        md=textwrap.dedent('''
        `> WHOAMI` \\[_Задание для проверки системы_]
        
        Напишите функцию `whoami()`, не принимающую аргументов и просто выводящую ваши ФИО (как 
        в табличке курса)
        ''')
    ),
    include=[],
    locator=FnLocator('whoami'),
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=WhoamiChecker(),
    tests=[
        ArgList()
    ],
    solution=None,
    executor=SUBSTITUTE_STDOUT,
    extended_info=True
)
