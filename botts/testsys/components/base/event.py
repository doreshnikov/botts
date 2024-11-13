from dataclasses import dataclass
from datetime import datetime

from botts.db.student import Student
from .task import Task
from .code import CodeUnit


EVENTS: dict[str, 'Event'] = {}


@dataclass
class Event:
    id_: str
    start: datetime
    deadline: datetime
    tasks: list[Task]
    
    def __post_init__(self):
        EVENTS[self.id_] = self
    
    @property
    def is_expired(self):
        return self.deadline < datetime.now()

    def render_statement(self) -> str:
        separator = '\n'
        return separator.join(map(lambda task: task.statement.md, self.tasks))


@dataclass
class Submission:
    event: Event
    task: Task
    author: Student
    solution: CodeUnit