from dataclasses import dataclass, field
from random import Random
from typing import Any, Callable

from .units import CodeUnit
from ..check.checker import Checker
from ..check.executor import Executor
from ..check.generator import generate, Generator
from ..check.validator import Validator
from ..extract.jupyter import Locator


@dataclass
class Statement:
    md: str | None = field(default=None)
    html: str | None = field(default=None)


@dataclass
class Task:
    id_: str
    locator: Locator
    include: list[CodeUnit]
    validator: Validator
    checker: Checker
    tests: list[Generator | Any]
    solution: Callable[[...], Any] | None
    statement: Statement = field(default_factory=Statement)
    time_limit: int = field(default=1)
    executor: Executor | None = None
    extended_info: bool = False

    def generate_tests(self, random: Random):
        return [generate(test, random) for test in self.tests]
