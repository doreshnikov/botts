from dataclasses import dataclass, field
from random import Random
from typing import Any, Callable

from .units import CodeUnit
from ..check.checker import Checker
from ..check.generator import generate, Generator
from ..check.validator import Validator
from ..extract.jupyter import Locator


@dataclass
class Task:
    id_: str
    locator: Locator
    include: list[CodeUnit]
    validator: Validator
    checker: Checker
    tests: list[Generator | Any]
    solution: Callable[[...], Any] | None
    time_limit: int = field(default=1)

    def generate_tests(self, random: Random):
        return [generate(test, random) for test in self.tests]
