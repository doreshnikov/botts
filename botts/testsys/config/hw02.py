import math
import numbers
import re
from datetime import datetime
from typing import Any

from ..components.base.include import inc
from ..components.base.task import Task
from ..components.check.checker import Checker, SequenceOf, Result, SINGLE_FLOAT_4, SINGLE_FLOAT_6, SINGLE_STRING, \
    Verdict
from ..components.check.generator import ArgList, Arguments, H, R_INT, R_FLOAT
from ..components.check.validator import NO_EVAL, NO_EXEC, NO_IMPORTS, NO_RECURSION, REQ_RECURSION
from ..components.extract.jupyter import FnLocator
from ..components.test.event import Event


def triangle_area(a, b, c):
    v1x, v1y = b[0] - a[0], b[1] - a[1]
    v2x, v2y = c[0] - a[0], c[1] - a[1]
    value = (v1x * v2y - v2x * v1y) / 2
    return abs(value)


def angle(a, b, c):
    v1x, v1y = a[0] - b[0], a[1] - b[1]
    v2x, v2y = c[0] - b[0], c[1] - b[1]
    y = v1x * v2y - v2x * v1y
    x = v1x * v2x + v1y * v2y
    return abs(math.degrees(math.atan2(y, x)))


def normal_cdf(x, mu, sigma):
    return 0.5 * (1 + math.erf((x - mu) / sigma / math.sqrt(2)))


def highest_point(m, alpha, v):
    g = 9.81
    return (v * math.sin(math.radians(alpha))) ** 2 / 2 / g


def travel_distance(m, alpha, v):
    g = 9.81
    return v * v * math.sin(2 * math.radians(alpha)) / g


def polynomial_add(p, q):
    r = [0.0 for _ in range(max(len(p), len(q)))]
    for i, pi in enumerate(p):
        r[i] += pi
    for i, qi in enumerate(q):
        r[i] += qi
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


def polynomial_to_string(p):
    p = list(map(float, p))

    def monomial_to_string(coeff: float, d: int) -> str:
        if d == 0:
            return f'{coeff}'
        cstr = f'{coeff}'
        if abs(coeff) == 1:
            cstr = '' if coeff == 1 else '-'
        if d == 1:
            return f'{cstr}x'
        return f'{cstr}x^{d}'

    monomials = []
    for d in reversed(range(len(p))):
        if p[d] == 0:
            continue
        monomials.append(monomial_to_string(p[d], d))
    result = ' + '.join(monomials)
    return result.replace(' + -', ' - ')


def polynomial_to_latex(p):
    p = list(map(float, p))

    def monomial_to_string(coeff: float, d: int) -> str:
        if d == 0:
            return f'{coeff}'
        cstr = f'{coeff}'
        if abs(coeff) == 1:
            cstr = '' if coeff == 1 else '-'
        if d == 1:
            return f'{cstr}x'
        return f'{cstr}x^{{{d}}}'

    monomials = []
    for d in reversed(range(len(p))):
        if p[d] == 0:
            continue
        monomials.append(monomial_to_string(p[d], d))
    result = ' + '.join(monomials)
    return '$' + result.replace(' + -', ' - ') + '$'


class StringChecker(Checker):
    @staticmethod
    def simplify(s: str):
        s = re.sub(r'\.0+[x$]', 'x', s)
        s = re.sub(r'\.0+$', '', s)
        return s

    def check(self, _: Any, output: Any, answer: str) -> Result:
        if not isinstance(output, str):
            return Result(Verdict.IA, f"expected a string, got '{output}'")
        output = StringChecker.simplify(output)
        answer = StringChecker.simplify(answer)
        if output != answer:
            return Result(Verdict.WA, f"something isn't right in '{output}', expected '{answer}'")
        return Result(Verdict.OK, None)


class LatexChecker(Checker):
    @staticmethod
    def simplify(s: str):
        s = re.sub(r'\^\{1}', r'^1', s)
        s = re.sub(r'\{(\d)}', r'\g<1>', s)
        s = re.sub(r'\.0+x', 'x', s)
        s = re.sub(r'\.0+\$', '$', s)
        s = re.sub(r'\s', '', s)
        return s

    def check(self, _: Any, output: Any, answer: str) -> Result:
        if not isinstance(output, str):
            return Result(Verdict.IA, f"expected a string, got '{output}'")
        output = LatexChecker.simplify(output)
        answer = LatexChecker.simplify(answer)
        if output != answer:
            return Result(Verdict.WA, f"something isn't right in '{output}', expected '{answer}'")
        return Result(Verdict.OK, None)


def polynomial_derivative(p):
    r = [p[i] * i for i in range(len(p))]
    if len(r) == 1:
        return [0]
    return r[1:]


def polynomial_divide(p, q):
    quot, rem = [], []
    while len(q) > 0 and q[-1] == 0:
        q.pop()
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    while len(p) >= len(q):
        divv = p[-1] / q[-1]
        for i in range(len(q)):
            p[-i - 1] -= q[-i - 1] * divv
        p.pop()
        quot.append(divv)

    quot.reverse()
    while len(p) > 0 and p[-1] == 0:
        p.pop()
    if len(p) == 0:
        p.append(0)
    return quot, p


def polynomial_from_string(s: str):
    items = ['+']
    if s.startswith('-'):
        items[0] = '-'
        s = s[1:]
    items += s.split()

    p = [0 for _ in range(len(items) // 2)]
    for i in range(len(items) // 2):
        sign = 1 if items[2 * i] == '+' else -1
        value = items[2 * i + 1].split('^')
        d = int(value[1]) if len(value) > 1 else (1 if 'x' in value[0] else 0)
        coeff = value[0][:value[0].find('x')]
        if coeff == '':
            coeff = '1'

        while d >= len(p):
            p.append(0)
        p[d] = float(coeff) * sign

    return p


def polynomial_multiply(p, q):
    r = [0.0 for _ in range(len(p) + len(q) - 1)]
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            r[i + j] += p[i] * q[j]
    return r


def polynomial_calculate(p, x: float | int) -> float:
    value = 0
    power_of_x = 1
    for i, pi in enumerate(p):
        value += pi * power_of_x
        power_of_x *= x
    return value


class FindRootChecker(Checker):
    def check(self, input_: Arguments, output: Any, _: Any) -> Result:
        if not isinstance(output, numbers.Number):
            return Result(Verdict.IA, f"expected a number, got '{output}'")
        # noinspection PyTypeChecker
        value = polynomial_calculate(*input_.args, output)
        if abs(value) > 0.0001:
            return Result(Verdict.WA, f"{output} is not a root: f(x) = {value}")
        return Result(Verdict.OK, None)


def recurrent_f(x):
    return x if x < 2 else 2 * recurrent_f(x ** 0.5) + 2 * x - 1


def solve_hanoi(i, j, n):
    if n == 1:
        return [f'{i} -> {j}']

    k = 3 - i - j
    actions = []
    actions += solve_hanoi(i, k, n - 1)
    actions.append(f'{i} -> {j}')
    actions += solve_hanoi(k, j, n - 1)
    return actions


def approximation(a, k, n):
    x = 1.0
    for i in range(n):
        x = ((k - 1) * x + a / (x ** (k - 1))) / k
    return x


R_POINT = R_FLOAT(-100.0, 100.0).repeat(2)

HW02 = Event(
    'Homework 02',
    datetime(year=2023, month=11, day=5, minute=0, second=0),
    [
        Task(
            id_='1-1-triangle-area',
            locator=FnLocator('triangle_area'),
            include=[
                inc('import math'),
                inc('point = tuple[float, float]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)),
                ArgList((0.0, 0.0), (5.0, 5.0), (10.0, 10.0)),
                *H.repeat_test(
                    ArgList(R_POINT, R_POINT, R_POINT),
                    8
                )
            ],
            solution=triangle_area
        ),
        Task(
            id_='1-2-angle',
            locator=FnLocator('angle'),
            include=[
                inc('import math'),
                inc('point = tuple[float, float]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SINGLE_FLOAT_4,
            tests=[
                ArgList((0.0, 0.0), (3.3, 0.0), (0.0, 3.3)),
                ArgList((-2.0, -2.0), (0.0, 0.0), (5.0, 5.0)),
                ArgList((-2.0, 2.0), (0.0, 0.0), (4.0, -4.0)),
                *H.repeat_test(
                    ArgList(R_POINT, R_POINT, R_POINT).retry_until(H.distinct),
                    7
                )
            ],
            solution=angle
        ),
        Task(
            id_='1-3-normal-cdf',
            locator=FnLocator('normal_cdf'),
            include=[
                inc('import math')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(42.0, 42.0, 13.0),
                ArgList(32.0, 42.0, 13.0),
                *H.repeat_test(
                    ArgList(R_FLOAT(-10.0, 10.0), R_FLOAT(-10.0, 10.0), R_FLOAT(0.1, 4.0)),
                    4
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(-100.0, 100.0), R_FLOAT(-10.0, 10.0), R_FLOAT(0.1, 10.0)),
                    4
                )
            ],
            solution=normal_cdf
        ),
        Task(
            id_='1-5-highest-point',
            locator=FnLocator('highest_point'),
            include=[
                inc('import math'),
                inc('g = 9.81')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(12.0, 45.0, 10.0),
                ArgList(10.0, 90.0, 10.0),
                *H.repeat_test(
                    ArgList(R_FLOAT(0.1, 100.0), R_FLOAT(0.1, 179.9), R_FLOAT(0.1, 100.0)),
                    number=13
                )
            ],
            solution=highest_point
        ),
        Task(
            id_='1-6-travel-distance',
            locator=FnLocator('travel_distance'),
            include=[
                inc('import math'),
                inc('g = 9.81')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(12.0, 45.0, 10.0),
                ArgList(10.0, 90.0, 10.0),
                *H.repeat_test(
                    ArgList(R_FLOAT(0.1, 100.0), R_FLOAT(0.1, 179.9), R_FLOAT(0.1, 100.0)),
                    number=13
                )
            ],
            solution=travel_distance
        ),
        Task(
            id_='2-0-add-modified',
            locator=FnLocator('add'),
            include=[
                inc('polynomial = list[float | int]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SequenceOf(SINGLE_FLOAT_6),
            tests=[
                ArgList([3, 0, 2], [-1, 0, -2]),
                ArgList([1] + [0 for _ in range(10)], [1, -1] + [0 for _ in range(9)]),
                ArgList([100.5, -10.5, 12.5, 33.1], [-100, 10, -12]),
                ArgList([1, 2, 3, 4], [-1, -2, -3, -4]),
                *H.repeat_test(
                    ArgList(
                        R_FLOAT(-100.0, 100.0).repeat(20, as_type=list),
                        R_FLOAT(-100.0, 100.0).repeat(30, as_type=list)
                    ),
                    number=4
                ),
                *H.repeat_test(
                    R_INT(30, 50).map(
                        lambda tail: R_INT(0, 5).map(
                            lambda size: R_FLOAT(-100.0, 100.0).repeat(tail, as_type=list).map(
                                lambda t: ArgList(
                                    R_FLOAT(-100.0, 100.0).repeat(size, as_type=list).map(
                                        lambda it: it + t
                                    ),
                                    R_FLOAT(-100.0, 100.0).repeat(size, as_type=list).map(
                                        lambda it: it + [-x for x in t]
                                    )
                                )
                            )
                        )
                    ),
                    number=12
                )
            ],
            solution=polynomial_add
        ),
        Task(
            id_='2-1-1-to-string',
            locator=FnLocator('to_string'),
            include=[
                inc('polynomial = list[float | int]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=StringChecker(),
            tests=[
                ArgList([0, 2, -1, 5]),
                ArgList([-5, -1.0, 1.0, 0.0, 1, 2, 3, -1.0, 1]),
                *H.repeat_test(
                    ArgList(R_INT(10, 20).map(
                        lambda size: R_FLOAT(-12.0, 12.0).map(
                            lambda x: -1.0 if x < -9 else (1.0 if x > 9 else (0.0 if abs(x) < 1 else x))
                        ).repeat(size, as_type=list)
                    )),
                    number=12
                )
            ],
            solution=polynomial_to_string
        ),
        Task(
            id_='2-1-2-to-latex',
            locator=FnLocator('to_latex'),
            include=[
                inc('polynomial = list[float | int]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=LatexChecker(),
            tests=[
                ArgList([0, 2, -1, 5]),
                ArgList([-5, -1.0, 1.0, 0.0, 1, 2, 3, -1.0, 1]),
                *H.repeat_test(
                    ArgList(R_INT(10, 20).map(
                        lambda size: R_FLOAT(-12.0, 12.0).map(
                            lambda x: -1.0 if x < -9 else (1.0 if x > 9 else (0.0 if abs(x) < 1 else x))
                        ).repeat(size, as_type=list)
                    )),
                    number=12
                )
            ],
            solution=polynomial_to_latex
        ),
        Task(
            id_='2-2-derivative',
            locator=FnLocator('derivative'),
            include=[
                inc('polynomial = list[float | int]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SequenceOf(SINGLE_FLOAT_6),
            tests=[
                ArgList([0, 2, -1, 5]),
                ArgList([-5, -1, 1, 0, 1, 2, 3, -1, 1]),
                ArgList([1]),
                *H.repeat_test(
                    ArgList(R_INT(10, 30).map(lambda size: R_FLOAT(-100.0, 100.0).repeat(size, as_type=list))),
                    number=12
                )
            ],
            solution=polynomial_derivative
        ),
        Task(
            id_='2-3-divide',
            locator=FnLocator('divide'),
            include=[
                inc('polynomial = list[float | int]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SequenceOf(SequenceOf(SINGLE_FLOAT_6), as_type=tuple),
            tests=[
                ArgList([2, 1, 3, 2], [6, 0, 3]),
                ArgList([100.5, -10.5, 12.5, 33.1], [-100, 10, -12]),
                ArgList([1, 2, 3, 4], [-1, -2, -3, -4]),
                ArgList([1], [1]),
                *H.repeat_test(
                    ArgList(
                        R_FLOAT(-100.0, 100.0).repeat(30, as_type=list).map(lambda t: t + [1.0]),
                        R_FLOAT(-100.0, 100.0).repeat(20, as_type=list).map(lambda t: t + [1.0])
                    ),
                    number=11
                )
            ],
            solution=polynomial_divide,
            time_limit=3
        ),
        Task(
            id_='2-4-from-string',
            locator=FnLocator('from_string'),
            include=[
                inc('polynomial = list[float | int]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=SequenceOf(SINGLE_FLOAT_6),
            tests=[
                ArgList('1'),
                ArgList('-x^4'),
                ArgList('2x^3'),
                ArgList('-x^5 + 4x^3 - x + 7.0'),
                ArgList('-x^5 + 4x^3'),
                ArgList(polynomial_to_string([-5, -1.0, 1.0, 0.0, 1, 2, 3, -1.0, 1])),
                *H.repeat_test(
                    ArgList(R_INT(10, 20).map(
                        lambda size: R_FLOAT(-12.0, 12.0).map(
                            lambda x: -1.0 if x < -9 else (1.0 if x > 9 else (0.0 if abs(x) < 1 else x))
                        ).repeat(size, as_type=list).map(
                            lambda it: polynomial_to_string(it if it[-1] != 0 else it + [1])
                        )
                    )),
                    number=14
                )
            ],
            solution=polynomial_from_string
        ),
        Task(
            id_='2-5-find-root',
            locator=FnLocator('find_root'),
            include=[
                inc('import math'),
                inc('polynomial = list[float | int ]')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=FindRootChecker(),
            tests=[
                ArgList([1, 2, 1]),
                ArgList([-10, 1]),
                *H.repeat_test(
                    R_INT(5, 10).map(
                        lambda size: R_FLOAT(-10.0, 10.0).repeat(size, as_type=list).map(
                            lambda it: R_FLOAT(-100.0, 100.0).map(
                                lambda x: ArgList(polynomial_multiply(it, [-x, 1]))
                            )
                        )
                    ),
                    number=13
                )
            ],
            solution=None
        ),
        Task(
            id_='3-1-recurrent',
            locator=FnLocator('f'),
            include=[
                inc('import math')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(1),
                ArgList(2),
                ArgList(144),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.0, 1e5)),
                    number=6
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(1e8, 1e9)),
                    number=6
                )
            ],
            solution=recurrent_f
        ),
        Task(
            id_='3-2-hanoi',
            locator=FnLocator('solve_hanoi'),
            include=[],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION,
            checker=SequenceOf(SINGLE_STRING),
            tests=[
                ArgList(0, 2, 4),
                *H.repeat_test(
                    R_INT(0, 2).repeat(2).retry_until(H.distinct).map(
                        lambda ij: R_INT(1, 12).map(
                            lambda n: ArgList(ij[0], ij[1], n)
                        )
                    ),
                    number=20
                )
            ],
            solution=solve_hanoi
        ),
        Task(
            id_='3-3-1-rec-approximation',
            locator=FnLocator('recursive_approximation'),
            include=[
                inc('from sys import setrecursionlimit\n'
                    'setrecursionlimit(100000)')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & REQ_RECURSION,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(10.0, 178324.0, 10000),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1.0, 1e5), 2),
                    number=7
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1e5, 1e9), 10000),
                    number=7
                )
            ],
            solution=approximation
        ),
        Task(
            id_='3-3-2-iter-approximation',
            locator=FnLocator('iterative_approximation'),
            include=[],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL & NO_RECURSION,
            checker=SINGLE_FLOAT_6,
            tests=[
                ArgList(10.0, 178324.0, 10000),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1.0, 1e5), 2),
                    number=7
                ),
                *H.repeat_test(
                    ArgList(R_FLOAT(1.5, 20.0), R_FLOAT(1e5, 1e9), 10000),
                    number=7
                )
            ],
            solution=approximation
        )
    ]
)
