import ast
import copy
import inspect
from random import Random
from typing import Awaitable, Callable

from botts.bot.config.local import report_fail
from botts.db.run import Run
from botts.db.submission import Submission
from .invoker_pool import FailedContainerException, INVOKER_POOL
from ..base.task import Task
from ..base.units import FnCodeUnit
from ..check.checker import Result, Verdict
from ..check.generator import Arguments


def safe_run(fn: Callable, input_: Arguments):
    try:
        args = copy.deepcopy(input_.args)
        kwargs = copy.deepcopy(input_.kwargs)
        result = fn(*args, **kwargs)
    except Exception as e:
        return e
    return result


class Runner:
    def __init__(self, task: Task):
        self.task = task
        self.solution = self.task.solution

    @staticmethod
    def solution_hash(source: ast.AST):
        return hash(ast.dump(source))

    def _do_run(self, source: str, **kwargs) -> Result:
        random = Random()
        submission_source = '\n'.join(
            [include.source for include in self.task.include] +
            [source]
        )
        tests = self.task.generate_tests(random)
        for i, test in enumerate(tests):
            answer = None
            if self.task.solution is not None:
                solution = self.task.solution
                if self.task.executor is not None:
                    solution = self.task.executor(solution)
                answer = safe_run(solution, test)
                if isinstance(answer, Exception):
                    return Result(Verdict.CF, f'[test {i + 1}] error while running correct solution: {answer}')

            invoker_id, invoker_port = None, None
            try:
                invoker = INVOKER_POOL.acquire()
                invoker_id, invoker_port = invoker.id_, invoker.port
                with invoker:
                    invoker.send({
                        'executor': (None if self.task.executor is None
                                     else inspect.getsource(self.task.executor)),
                        'source': submission_source,
                        'args': test.args,
                        'time_limit': self.task.time_limit
                    })
                    result = invoker.receive()
            except FailedContainerException as e:
                report_fail(f'Invoker failed:\n```{e.logs.decode("utf-8")}```')
                return Result(Verdict.CF, 'invoker failed', invoker_id, invoker_port)

            if 'error' in result:
                cause = f'[test {i + 1}] {result["error"]}'
                return Result(Verdict.CF, cause, invoker_id, invoker_port)
            if result['verdict'] != 'OK':
                cause = f'[test {i + 1}] {result["message"]}'
                return Result(Verdict[result['verdict']], cause, invoker_id, invoker_port)
            output = result['value']

            check_result = self.task.checker.check(test, output, answer, **kwargs)
            if check_result.verdict != Verdict.OK:
                check_result.cause = f'[test {i + 1}] {check_result.cause}'
                check_result.invoker_id = invoker_id
                check_result.invoker_port = invoker_port
                return check_result
        return Result(Verdict.OK, None)

    def store(
            self, source: FnCodeUnit, submission: Submission,
            result: Result
    ):
        Run.create(
            task_id=self.task.id_,
            solution_source=source.source,
            solution_hash=Runner.solution_hash(source.node),
            submission=submission,
            verdict=result.verdict.name,
            comment=result.cause,
            invoker_id=result.invoker_id,
            invoker_port=result.invoker_port
        )

    def run(self, submission: Submission, source: FnCodeUnit) -> Result:
        kwargs = {}
        if self.task.extended_info:
            kwargs['student_id'] = submission.student.id_
        result = self._do_run(source.source, **kwargs)
        self.store(source, submission, result)
        return result

    @staticmethod
    async def rejudge(
            runs: list[Run], task_resolver,
            step_callback: Callable[[...], Awaitable], final_callback: Callable[[...], Awaitable]
    ):
        results: dict[int, Result] = {}
        try:
            for run in runs:
                submission = run.submission
                event = submission.event
                task = task_resolver(event, run.task_id)
                if task is None:
                    run.verdict = Verdict.CF.name
                    run.comment = 'task not found'
                    run.save()
                    results[run.id_] = Result(Verdict.CF, run.comment)
                    continue

                solution = run.solution_source
                solution_ast = ast.parse(solution)
                for node in ast.walk(solution_ast):
                    if isinstance(node, ast.FunctionDef):
                        solution_ast = node
                        break
                if message := task.validator.validate(FnCodeUnit(solution, solution_ast)):
                    results[run.id_] = Result(Verdict.VE, message)
                    run.verdict = Verdict.VE.name
                    run.comment = message
                    run.save()
                    await step_callback(results)
                    continue

                result = Runner(task)._do_run(solution)
                results[run.id_] = result
                run.verdict = result.verdict.name
                run.comment = result.cause
                run.invoker_id = result.invoker_id
                run.invoker_port = result.invoker_port
                run.save()
                await step_callback(results)
        finally:
            await final_callback(results)
