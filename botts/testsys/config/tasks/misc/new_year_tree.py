import textwrap
from typing import Any

from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import Checker, Result, Verdict
from botts.testsys.components.check.generator import ArgList
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.check.executor import SUBSTITUTE_STDOUT
from botts.testsys.components.extract.jupyter import FnLocator


def solution(n: int):
    tree = [
        [' ' for _ in range(2 * (n + 1))]
        for _ in range((n + 1) * (n + 2) // 2 + 1)
    ]

    tree[0][n], tree[0][n + 1] = '<', '>'
    tree[-1][n], tree[-1][n + 1] = '|', '|'

    r = 1
    for i in range(2, n + 2):
        for j in range(i):
            tree[r][n - j], tree[r][n + 1 + j] = '/', '\\'
            r += 1
        for j in range(-i + 2, i):
            tree[r - 1][n + j] = '_'

    for row in tree:
        print(''.join(row))


class TreeChecker(Checker):
    CHARS = ['<', '>', '\\', '/', '|', '_', ' ']

    @staticmethod
    def cleanup(tree: str) -> list[str]:
        rows = [row.rstrip() for row in tree.rstrip().split('\n')]
        while len(rows) > 0 and len(rows[-1].strip()) == 0:
            rows.pop()
        return rows

    def check(self, _: Any, out_data: str, answer: str) -> Result:
        pa = self.cleanup(out_data)
        ja = self.cleanup(answer)
        if len(pa) != len(ja):
            return Result(Verdict.WA, f'expected {len(ja)} rows, got {len(pa)}')
        for i in range(len(pa)):
            if len(pa[i]) != len(ja[i]):
                return Result(Verdict.WA, f'expected {len(ja[i])} chars in row {i + 1}, got {len(pa[i])}')
            for j in range(len(pa[i])):
                if pa[i][j] not in TreeChecker.CHARS:
                    continue
                if pa[i][j] != ja[i][j]:
                    return Result(Verdict.WA, f'expected \'{ja[i][j]}\' on row {i + 1}, position {j + 1}, '
                                              f'got \'{pa[i][j]}\'')
        return Result(Verdict.OK, None)


TASK = Task(
    id_='happy-new-year',
    statement=Statement(
        md=textwrap.dedent('''
        `> HAPPY NEW YEAR`
        
        Напишите функцию `happy_new_year(n)`, выводящую новогоднюю елку из `n` сегментов.
        
        Иными словами, функция на вход получает число сегментов `n`, и вам надо вывести
         - звездочку наверху, 
         - сегменты размерами от `2` до `n + 1`, 
        - и в конце – ножку ствола. 
        
        Каждый следующий сегмент должен начинаться ровно в середине предыдущего и быть 
        размером на один больше предыдущего. Можете так же украсить елку любыми игрушками 
        внутри (`$`, `#`, `@`), но это не обязательно. Выводить пробелы в конце строк тоже 
        не обязательно.
        
        Пример для `n = 3`:
        ```
           <>
           /\\
          /__\\
           /\\
          /$ \\
         /____\\
           /\\
          /@ \\
         /   #\\
        /______\\
           ||
        ```

        **Рекомендация**: будет проще выписать на бумажке формулу того, какие по порядку 
        строки и позиции в строке занимают определенные символы каждого сегмента, завести 
        матрицу символов нужного размера, заполнить ее, а потом склеить ее в строки и вывести.
        ''')
    ),
    locator=FnLocator('happy_new_year'),
    include=[],
    validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
    checker=TreeChecker(),
    tests=[
        ArgList(i) for i in range(1, 15)
    ],
    solution=solution,
    executor=SUBSTITUTE_STDOUT,
    time_limit=20
)