import numbers
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(Enum):
    MS = "Missing"
    CF = "Check Failed"
    VE = "Validation Error"
    IA = "Invalid Answer"
    WA = "Wrong Answer"
    RE = "Runtime Error"
    TL = "Time Limit Exceeded"
    OK = "Correct"


@dataclass
class Result:
    verdict: Verdict
    cause: str | None
    invoker_id: str | None = field(default=None)
    invoker_port: str | None = field(default=None)


class Checker(ABC):
    @abstractmethod
    def check(self, input_: Any, output: Any, answer: Any) -> Result:
        pass


class Exact(Checker):
    def __init__(self, expected_type: type, type_repr: str):
        self.expected_type = expected_type
        self.type_repr = type_repr

    def check(self, _: Any, output: Any, answer: Any) -> Result:
        if not isinstance(output, self.expected_type):
            return Result(Verdict.IA, f"expected a {self.type_repr}, got '{type(output)}'")
        if output != answer:
            return Result(Verdict.WA, f"expected '{answer}', got '{output}'")
        return Result(Verdict.OK, None)


SINGLE_NUMBER = Exact(numbers.Number, 'number')
SINGLE_STRING = Exact(str, 'string')


class CloseNumbers(Checker):
    def __init__(self, delta: float):
        self.delta = delta

    def check(self, _: Any, output: Any, answer: Any) -> Result:
        if not isinstance(output, numbers.Number):
            return Result(Verdict.IA, f"expected a number, got '{output}'")
        # noinspection PyUnresolvedReferences
        if abs(output - answer) > self.delta:
            return Result(Verdict.WA, f"expected '{answer}', got '{output}'")
        return Result(Verdict.OK, None)


SINGLE_FLOAT_6 = CloseNumbers(1e-6)
SINGLE_FLOAT_4 = CloseNumbers(1e-4)


class SequenceOf(Checker):
    def __init__(self, sub_checker: Checker, as_type: type = list):
        self.sub_checker = sub_checker
        self.as_type = as_type

    def check(self, input_: Any, output: Any, answer: Any) -> Result:
        if not isinstance(output, self.as_type):
            return Result(Verdict.IA, f"expected a list, got '{output}'")
        if len(output) != len(answer):
            return Result(Verdict.WA, f"expected a list of size {len(answer)}, got {len(output)}")
        for i, pair_ in enumerate(zip(output, answer)):
            out, ans = pair_
            result = self.sub_checker.check(input_, out, ans)
            if result.verdict != Verdict.OK:
                result.cause = f'on position {i + 1}: {result.cause}'
                return result
        return Result(Verdict.OK, None)
