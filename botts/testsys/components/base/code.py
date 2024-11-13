import ast
from dataclasses import dataclass



@dataclass
class CodeUnit:
    source: str
    node: ast.AST
