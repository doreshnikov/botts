from datetime import datetime
from typing import Awaitable, Callable

from botts.db.submission import Submission
from .runner import Runner
from ..base.task import Task, Statement
from ..check.checker import Result, Verdict
from ..extract.jupyter import NotebookContainer


class Event:
    ALL: dict[str, 'Event'] = {}

    def __init__(self, name: str, start: datetime, deadline: datetime, tasks: list[Task], *, statement_prefix: Statement | None = None):
        self.name = name
        self.start = start
        self.deadline = deadline
        self.tasks = tasks
        self.id_ = name.lower().replace(' ', '-')
        self.statement_prefix = statement_prefix
        Event.ALL[self.id_] = self

    @property
    def is_expired(self):
        return self.deadline < datetime.now()

    @staticmethod
    def resolve_task(event: str, task_id: str):
        task_options = [t for t in Event.ALL[event].tasks if t.id_ == task_id]
        if len(task_options) == 0:
            return None
        return task_options[0]

    def render_statement(self) -> str:
        separator = ''
        items = list(map(lambda task: task.statement.md, self.tasks))
        if self.statement_prefix is not None:
            items = [self.statement_prefix.md] + items
        return separator.join(items)

    async def run(
            self, container: NotebookContainer, submission: Submission,
            step_callback: Callable[[...], Awaitable], final_callback: Callable[[...], Awaitable]
    ):
        results: dict[str, Result] = {}
        try:
            collect_report = container.collect([task.locator for task in self.tasks])
            solutions = collect_report.data

            for task in self.tasks:
                runner = Runner(task)

                if task.locator not in solutions:
                    results[task.id_] = Result(Verdict.MS, None)
                    await step_callback(results)
                    continue

                solution = solutions[task.locator]
                if message := task.validator.validate(solution):
                    result = Result(Verdict.VE, message)
                    results[task.id_] = result
                    runner.store(solution, submission, result)
                    await step_callback(results)
                    continue

                results[task.id_] = Runner(task).run(submission, solution)
                await step_callback(results)
        finally:
            await final_callback(results)
