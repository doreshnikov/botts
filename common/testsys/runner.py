import ast

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(Enum):
    MS = "Missing"
    CF = "Check Failed"
    VE = "Validation Error"
    IA = "Invalid Answer"
    WA = "Wrong Answer"
    CE = "Compile Error"
    RE = "Runtime Error"
    TL = "Time Limit Exceeded"
    OK = "Correct"


@dataclass
class JudgeSignature:
    id_: str
    port: int
    
    
@dataclass(frozen=False)
class JudgeFeedback:
    verdict: Verdict
    message: str | None


@dataclass
class TestingRequest:
    source: str
    args: tuple[object]
    kwargs: dict[str, object]
    time_limit: int = field(default=1)
    

@dataclass
class TestingResponse:
    verdict: Verdict
    message: str | None
    value: object


@dataclass(frozen=False)
class TestingResult:
    feedback: JudgeFeedback
    value: Any = field(default=None)
    signature: JudgeSignature | None = field(default=None)



def evaluate(source: ast.AST, fn_name: str, args: tuple) -> TestingResponse:
    fn_name = None
    for node in ast.walk(source):
        if isinstance(node, ast.FunctionDef):
            fn_name = node.name
            break
    if fn_name is None:
        return TestingResponse(Verdict.MS, message='no function definition found')

    if not isinstance(source, ast.Module):
        source = ast.Module(body=[source])

    try:
        code = compile(source, filename='<ast>', mode='exec')
        evaluate = ast.parse(f'{fn_name}(*args)', mode='eval')
        expr = compile(evaluate, filename='<ast>', mode='eval')
    except SyntaxError as e:
        return TestingResponse(Verdict.CE, message=f'could not compile: \'{e}\'')

    _globals = {}
    try:
        exec(code, _globals)
    except Exception as e:
        return TestingResponse(Verdict.CE, message=f'could not run definition: \'{e}\'')
    
    try:
        value = eval(expr, _globals, {'args': args})
        return TestingResponse(Verdict.OK, value=value)
    except Exception as e:
        return TestingResponse(Verdict.RE, message=f'runtime error \'{e}\'')