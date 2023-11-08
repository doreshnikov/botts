import ast
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from botts.testsys.components.base.units import FnCodeUnit


class Locator(ABC):
    @abstractmethod
    def matches(self, node: ast.AST) -> bool:
        pass

    @abstractmethod
    def __hash__(self):
        pass


class FnLocator(Locator):
    def __init__(self, name: str):
        self.name = name

    def matches(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.FunctionDef):
            return False
        return node.name == self.name

    def __hash__(self):
        return hash(f'<function:{self.name}>')


class NotebookContainer:
    def __init__(self, content: dict):
        self.content = content
        if 'cells' not in content:
            raise ValueError('no \'cells\' field found in .json-like content')

    @staticmethod
    def _collect_cell(cell: list[str]):
        return ''.join(cell)

    def __iter__(self) -> Iterator[str]:
        return map(
            lambda cell: NotebookContainer._collect_cell(cell['source']),
            iter([
                item
                for item in self.content['cells']
                if isinstance(item, dict) and item.get('cell_type') == 'code'
            ])
        )

    @dataclass
    class CollectReport:
        malformed_source: dict[int, SyntaxError] = field(default_factory=dict)
        ignored_repeats: dict[Locator, int] = field(default_factory=dict)
        data: dict[Locator, FnCodeUnit] = field(default_factory=dict)

    def collect(self, locators: list[Locator]):
        preprocess = {
            locator.name: locator
            for locator in locators
            if isinstance(locator, FnLocator)
        }  # TODO rewrite in more generic way

        report = NotebookContainer.CollectReport()
        for i, cell in enumerate(self):
            try:
                tree = ast.parse(cell)
            except SyntaxError as e:
                report.malformed_source[i] = e
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                if node.name in preprocess:
                    loc = preprocess[node.name]
                    if loc in report.data:
                        report.ignored_repeats[loc] = report.ignored_repeats.get(loc, 0) + 1
                    else:
                        # noinspection PyTypeChecker
                        source = ast.get_source_segment(cell, node)
                        if source is None:
                            source = cell
                        # noinspection PyTypeChecker
                        report.data[loc] = FnCodeUnit(source, node)
        return report


if __name__ == '__main__':
    nc = NotebookContainer('resources/hw-02.ipynb')
    report = nc.collect([FnLocator('triangle_area'), FnLocator('normal_cdf')])
    print(report.malformed_source)
    print(report.ignored_repeats)
    print(report.data)
