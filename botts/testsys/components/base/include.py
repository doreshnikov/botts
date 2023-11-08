import ast

from .units import CodeUnit


def inc(code: str):
    return CodeUnit(code, ast.parse(code))
