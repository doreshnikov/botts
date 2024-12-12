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
class TestingResult:
    verdict: Verdict
    message: str | None
    value: Any = field(default=None)
