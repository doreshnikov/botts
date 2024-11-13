import ast

from .locator import Locator, FnLocator, CollectReport
from ..base.code import CodeUnit


class NotebookContainer:
    def __init__(self, content: dict):
        self.content = content
        if 'cells' not in content:
            raise ValueError('no \'cells\' field found in .json-like content')

    def parse(self) -> list[str]:
        return [
            ''.join(cell['source'])
            for cell in self.content['cells']
            if isinstance(cell, dict) and cell.get('cell_type') == 'code'
        ]

    def collect(self, locators: list[Locator]) -> CollectReport:
        report = CollectReport()
        
        for i, cell in enumerate(self):
            try:
                tree = ast.parse(cell)
            except SyntaxError as e:
                report.malformed_source[i] = e
                continue
            
            for node in ast.walk(tree):
                if node.__class__ not in Locator.ALLOWED_TYPES:
                    continue
                
                for locator in locators:
                    if not locator.matches(node):
                        continue
                    
                    if locator in report.data:
                        report.ignored_repeats[locator] = report.ignored_repeats.get(locator, 0) + 1
                        continue
                
                    # noinspection PyTypeChecker
                    source = ast.get_source_segment(cell, node)
                    if source is None:
                        source = cell
                    # noinspection PyTypeChecker
                    report.data[locator] = CodeUnit(source, node)

        return report


if __name__ == '__main__':
    nc = NotebookContainer('resources/hw-02.ipynb')
    report = nc.collect([FnLocator('triangle_area'), FnLocator('normal_cdf')])
    print(report.malformed_source)
    print(report.ignored_repeats)
    print(report.data)
