import ast
from abc import ABC, abstractmethod

from botts.testsys.components.base.units import CodeUnit
from botts.testsys.components.check.generator import Arguments
from common.testsys.runner import TestingResult, Verdict


class VerdictError(Exception):
    def __init__(self, verdict: Verdict, message: str):
        self.verdict = verdict
        self.message = message


class InvokerBase(ABC):
    @staticmethod
    def _handle_verdict_error(fn):
        def wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except VerdictError as e:
                return TestingResult(e.verdict, e.message, None)

        return wrapped

    @abstractmethod
    def invoke(self, source: str | CodeUnit, args: Arguments, time_limit: int | float,
               executor: str | None) -> TestingResult:
        pass


class ExecInvoker(InvokerBase):
    @staticmethod
    def _extract_function_name(source: str, on_fail: Verdict) -> str:
        try:
            code = ast.parse(source)
            fn_name = None
            for node in ast.walk(code):
                if isinstance(node, ast.FunctionDef):
                    fn_name = node.name
                    break
            return fn_name
        except SyntaxError as e:
            raise VerdictError(on_fail, e.text)

    @InvokerBase._handle_verdict_error
    def invoke(self, source: str | CodeUnit, args: Arguments, time_limit: int | float,
               executor: str | None) -> TestingResult:
        fn_name = ExecInvoker._extract_function_name(source, on_fail=Verdict.RE)
        if executor is not None:
            ex_name = ExecInvoker._extract_function_name(executor, on_fail=Verdict.CF)
            source = '\n'.join([
                source,
                executor,
                f'{fn_name} = {ex_name}({fn_name})'
            ])

        code = ast.parse(source)
        if not isinstance(code, ast.Module):
            code = ast.Module(body=[code])

        code = compile(code, filename='<ast>', mode='exec')
        expr = ast.parse(f'{fn_name}(*args)', mode='eval')
        expr = compile(expr, filename='<ast>', mode='eval')

        try:
            exec(code, globals())
        except Exception as e:
            raise VerdictError(Verdict.RE, f'Could not initialize function: \'{e}\'')
        try:
            value = eval(expr, {'fn_name': fn_name})
        except Exception as e:
            raise VerdictError(Verdict.RE, 'Runtime error: \'{e}\'')

        return TestingResult(Verdict.OK, 'Testing complete', value)
