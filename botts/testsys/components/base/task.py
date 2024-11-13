from dataclasses import dataclass, field
from random import Random
from typing import Callable

from ..process.check import Checker
from ..process.execute import Executor
from ..process.generate import generate, Generator, Arguments
from ..process.validate import Validator
from ..extract.jupyter import Locator


@dataclass
class Statement:
    md: str | None = field(default=None)
    html: str | None = field(default=None)


@dataclass
class Task:
    id_: str
    locator: Locator
    include: list[str]
    validator: Validator
    checker: Checker
    tests: list[Generator | object]
    solution: Callable[..., object] | None
    statement: Statement = field(default_factory=Statement)
    time_limit: int = field(default=1)
    executor: Executor | None = None
    extended_info: bool = False

    def generate_tests(self, random: Random) -> list[Arguments]:
        return [generate(test, random) for test in self.tests]
