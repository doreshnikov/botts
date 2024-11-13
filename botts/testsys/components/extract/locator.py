import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..base.code import CodeUnit


class Locator(ABC):
    ALLOWED_TYPES = [ast.FunctionDef, ast.ClassDef]
    
    @abstractmethod
    def matches(self, node: ast.AST) -> bool:
        pass


@dataclass
class CollectReport:
    malformed_source: dict[int, SyntaxError] = field(default_factory=dict)
    ignored_repeats: dict[Locator, int] = field(default_factory=dict)
    data: dict[Locator, CodeUnit] = field(default_factory=dict)


@dataclass(eq=True, frozen=True)
class FnLocator(Locator):
    name: str

    def matches(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.FunctionDef):
            return False
        return node.name == self.name
