import ast
from dataclasses import dataclass


@dataclass
class CodeUnit:
    source: str
    node: ast.AST


@dataclass
class FnCodeUnit:
    source: str
    node: ast.FunctionDef
