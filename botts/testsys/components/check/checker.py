import numbers
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable

from common.testsys.runner import Verdict


@dataclass
class Result:
    verdict: Verdict
    cause: str | None
    invoker_id: str | None = field(default=None)
    invoker_port: str | None = field(default=None)


class Checker(ABC):
    @abstractmethod
    def check(self, in_data: Any, out_data: Any, answer: Any, **kwargs) -> Result:
        pass


class _Anything(Checker):
    def check(self, _: Any, out_data: Any, answer: Any, **__) -> Result:
        if out_data != answer:
            return Result(Verdict.IA, f"expected '{answer}', got '{out_data}'")
        return Result(Verdict.OK, None)


class _VerboseChecker(Checker):
    def __init__(self, wrapped: Checker):
        super().__init__()
        self.checker = wrapped
    
    def check(self, in_data: Any, out_data: Any, answer: Any, **kwargs) -> Result:
        result = self.checker.check(in_data, out_data, answer, **kwargs)
        if result.verdict == Verdict.OK:
            return result
        return Result(result.verdict, f'Failed on {in_data}, expected {answer}, got {out_data}')
    

ANYTHING = _Anything()
VERBOSE = _VerboseChecker


class Exact(Checker):
    def __init__(self, expected_type: type, type_repr: str):
        self.expected_type = expected_type
        self.type_repr = type_repr

    def check(self, _: Any, out_data: Any, answer: Any, **__) -> Result:
        if not isinstance(out_data, self.expected_type):
            return Result(Verdict.IA, f"expected a {self.type_repr}, got '{type(out_data)}'")
        if out_data != answer:
            return Result(Verdict.WA, f"expected '{answer}', got '{out_data}'")
        return Result(Verdict.OK, None)


SINGLE_BOOL = Exact(bool, 'bool')
SINGLE_NUMBER = Exact(numbers.Number, 'number')
SINGLE_STRING = Exact(str, 'string')
BYTES = Exact(bytes, 'bytes')


class CloseNumbers(Checker):
    def __init__(self, delta: float):
        self.delta = delta

    def check(self, _: Any, out_data: Any, answer: Any, **__) -> Result:
        if not isinstance(out_data, numbers.Number):
            return Result(Verdict.IA, f"expected a number, got '{out_data}'")
        # noinspection PyUnresolvedReferences
        if abs(out_data - answer) > self.delta:
            return Result(Verdict.WA, f"expected '{answer}', got '{out_data}'")
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

    def check(self, in_data: Any, out_data: Any, answer: Any, **__) -> Result:
        if not isinstance(out_data, self.as_type):
            return Result(Verdict.IA, f"expected a list, got '{out_data}'")
        if len(out_data) != len(answer):
            return Result(Verdict.WA, f"expected a list of size {len(answer)}, got {len(out_data)}")
        sequence = zip(out_data, answer) if not self.sorted else zip(self.sort(out_data), self.sort(answer))
        for i, pair_ in enumerate(sequence):
            out, ans = pair_
            result = self.sub_checker.check(in_data, out, ans)
            if result.verdict != Verdict.OK:
                result.cause = f'on position {i + 1}: {result.cause}'
                return result
        return Result(Verdict.OK, None)


class DictOf(Checker):
    def __init__(self, key_checker: Checker, value_checker: Checker):
        self.key_checker = key_checker
        self.value_checker = value_checker

    def check(self, _: Any, out_data: Any, answer: dict, **__) -> Result:
        if not isinstance(out_data, dict):
            return Result(Verdict.IA, f"expected a dict, got '{out_data}'")
        if len(out_data) != len(answer):
            return Result(Verdict.WA, f"expected a dict of size {len(answer)}, got {len(out_data)}")
        for k1, v1 in out_data.items():
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

    def check(self, in_data: Any, out_data: Any, answer: Any, **__) -> Result:
        causes = []
        for sub_checker in self.sub_checkers:
            verdict = sub_checker.check(in_data, out_data, answer)
            causes.append(verdict.cause)
            if verdict.verdict == Verdict.OK:
                return verdict
        return Result(Verdict.WA, f'neither of specified checkers accepted the value: {", ".join(causes)}')
