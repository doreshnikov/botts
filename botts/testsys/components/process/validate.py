import ast
from abc import ABC, abstractmethod
from typing import Type

from botts.testsys.components.base.code import CodeUnit


class Validator(ABC):
    @abstractmethod
    def validate(self, unit: CodeUnit) -> str | None:
        pass

    def __and__(self, other):
        if not isinstance(other, Validator):
            raise ValueError('Validators can only be added together')

        class _CombinedValidator(Validator):
            def validate(_, unit: CodeUnit) -> str | None:
                check = self.validate(unit)
                if check is not None:
                    return check
                return other.validate(unit)

        return _CombinedValidator()


class NoNodeType(Validator):
    def __init__(self, node_type: Type[ast.AST], ignore_root: bool = True):
        self.node_type = node_type
        self.class_name = node_type.__name__
        self.ignore_root = ignore_root

    def validate(self, unit: CodeUnit) -> str | None:
        for node in ast.walk(unit.node):
            if self.ignore_root and node == unit.node:
                continue
            if isinstance(node, self.node_type):
                return f'no {self.class_name} statements allowed'
        return None


class NoFnCall(Validator):
    def __init__(self, fn_name: str):
        self.fn_name = fn_name

    def validate(self, unit: CodeUnit) -> str | None:
        for node in ast.walk(unit.node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == self.fn_name:
                return f'no calls to {self.fn_name}() allowed'
        return None


class NoNodeName(Validator):
    def __init__(self, name: str):
        self.name = name

    def validate(self, unit: CodeUnit) -> str | None:
        for node in ast.walk(unit.node):
            if isinstance(node, ast.Name) and node.id == self.name:
                return f'no name nodes with name \'{self.name}\' allowed'
        return None


NO_IMPORTS = NoNodeType(ast.Import) & NoNodeType(ast.ImportFrom) & NoNodeName('__import__')
NO_LOCAL_FUNCTIONS = NoNodeType(ast.FunctionDef)
NO_EXEC = NoFnCall('exec') & NoNodeName('exec')
NO_EVAL = NoFnCall('eval') & NoNodeName('eval')


class CheckRecursion(Validator):
    def __init__(self, require_recursion: bool):
        self.require_recursion = require_recursion

    def validate(self, unit: CodeUnit) -> str | None:
        unit_name = unit.node.name
        recursion_found = False
        for node in ast.walk(unit.node):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name):
                continue
            if node.func.id == unit_name:
                recursion_found = True
                break

        if self.require_recursion and not recursion_found:
            return 'recursion is required'
        if not self.require_recursion and recursion_found:
            return 'recursion is forbidden'
        return None


NO_RECURSION = CheckRecursion(False)
REQUIRE_RECURSION = CheckRecursion(True)
