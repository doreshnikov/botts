import json
import numbers
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


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
    def check(self, input_: Any, output: Any, answer: Any, **kwargs) -> Result:
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


SINGLE_BOOL = Exact(bool, 'bool')
SINGLE_NUMBER = Exact(numbers.Number, 'number')
SINGLE_STRING = Exact(str, 'string')
BYTES = Exact(bytes, 'bytes')


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
    def __init__(self, sub_checker: Checker, as_type: type = list, sorted: bool = True):
        self.sub_checker = sub_checker
        self.as_type = as_type
        self.sorted = sorted

    @staticmethod
    def sort(values: Iterable[Any]) -> Iterable[Any]:
        return sorted(values, key=repr)

    def check(self, input_: Any, output: Any, answer: Any) -> Result:
        if not isinstance(output, self.as_type):
            return Result(Verdict.IA, f"expected a list, got '{output}'")
        if len(output) != len(answer):
            return Result(Verdict.WA, f"expected a list of size {len(answer)}, got {len(output)}")
        sequence = zip(output, answer) if not self.sorted else zip(self.sort(output), self.sort(answer))
        for i, pair_ in enumerate(sequence):
            out, ans = pair_
            result = self.sub_checker.check(input_, out, ans)
            if result.verdict != Verdict.OK:
                result.cause = f'on position {i + 1}: {result.cause}'
                return result
        return Result(Verdict.OK, None)


class DictOf(Checker):
    def __init__(self, key_checker: Checker, value_checker: Checker):
        self.key_checker = key_checker
        self.value_checker = value_checker

    def check(self, _: Any, output: Any, answer: dict) -> Result:
        if not isinstance(output, dict):
            return Result(Verdict.IA, f"expected a dict, got '{output}'")
        if len(output) != len(answer):
            return Result(Verdict.WA, f"expected a dict of size {len(answer)}, got {len(output)}")
        for k1, v1 in output.items():
            ok = False
            for k2, v2 in answer.items():
                k_verdict = self.key_checker.check(_, k1, k2)
                v_verdict = self.value_checker.check(_, v1, v2)
                if k_verdict.verdict == Verdict.OK and v_verdict.verdict == Verdict.OK:
                    ok = True
                    break
            if not ok:
                return Result(Verdict.WA, f'no matching pair for ({k1}: {v1}) in answer')
        return Result(Verdict.OK, None)


class EitherOf(Checker):
    def __init__(self, *sub_checkers: Checker):
        self.sub_checkers = sub_checkers

    def check(self, input_: Any, output: Any, answer: Any) -> Result:
        causes = []
        for sub_checker in self.sub_checkers:
            verdict = sub_checker.check(input_, output, answer)
            causes.append(verdict.cause)
            if verdict.verdict == Verdict.OK:
                return verdict
        return Result(Verdict.WA, f'neither of specified checkers accepted the value: {", ".join(causes)}')
