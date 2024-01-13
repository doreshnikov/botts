from datetime import datetime
from random import Random
from sys import setrecursionlimit
from typing import Any

from ...components.base.task import Task
from ...components.check.checker import EitherOf, SequenceOf, SINGLE_BOOL, SINGLE_NUMBER, \
    SINGLE_STRING
from ...components.check.generator import ArgList, Arguments, Generator, H, R_INT, R_PERM
from ...components.check.validator import NO_EVAL, NO_EXEC, NO_IMPORTS, NoNameNode
from ...components.extract.jupyter import FnLocator
from ...components.test.event import Event

DEFAULT_VAL = NO_IMPORTS & NO_EXEC & NO_EVAL & NoNameNode('globals')

setrecursionlimit(100000)


def cats_and_mice(mapping):
    if mapping.find('C') == -1 or mapping.find('m') == -1:
        return 'We need two animals!'
    lst = mapping.split('\n')
    for ind, s in enumerate(lst):
        if 'C' in s:
            i, j = s.find('C'), ind
        if 'm' in s:
            k, l = s.find('m'), ind
    h, w = abs(k - i), abs(l - j)
    return h + w


class CatsAndMiceGenerator(Generator):
    def __init__(self, n: int):
        self.n = n

    def __call__(self, random: Random) -> Any:
        h, w = random.randint(4, self.n), random.randint(4, self.n)
        mapping = [["."] * w for _ in range(h)]

        if random.randint(1, 10) < 10:
            i, j = random.randint(0, h - 1), random.randint(0, w - 1)
            mapping[i][j] = "C"
        if random.randint(1, 10) < 10:
            i, j = random.randint(0, h - 1), random.randint(0, w - 1)
            mapping[i][j] = "m"

        return Arguments(
            args=("\n".join("".join(row) for row in mapping),),
            kwargs={}
        )


def exchange(lst):
    if not isinstance(lst[0], int) or not isinstance(lst[1], int):
        return 'invalid elements'
    s1, s2 = str(lst[0]), str(lst[1])
    s = s1 + s2
    s1, s2 = s[:len(s) // 2], s[len(s) // 2:]
    return abs(int(s1) - int(s2))


def sorting_cards(cards):
    lst = ['A', 'J', 'K', 'Q', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    cards = cards[:]
    cards.sort(key=lst.index)
    return cards


def check_password(s):
    return 'valid' if (5 <= len(s) <= 15 and
                       [i for i in s if i.isupper()] and
                       [i for i in s if i.islower()] and
                       [i for i in s if i in '!@#$%^&*?'] and
                       not [i for i in s if not i.isalnum() and i not in '!@#$%^&*?'] and
                       len([i for i in s if i.isalpha()]) >= 3 and
                       [i for i in s if i.isdigit()]) \
        else 'not valid'


def sorted_people(a):
    c = [i for i in a if i != -1]
    b = sorted(c, reverse=len(c) < len(a) - len(c))
    return [x if x == -1 else b.pop() for x in a]


def remove_doubles(s):
    s1 = ''
    s2 = ''
    for i in s:
        if s1 and i == s1[-1]:
            s1 = s1[:-1]
            s2 += i * 2
        else:
            s1 += i
    return s1, s2


def close_primes(x, y):
    def prime(x):
        if x < 2:
            return False
        i = 2
        while i * i <= x:
            if x % i == 0:
                return False
            i += 1
        return True

    cnt = 0
    for i in range(x, y + 1):
        if prime(i):
            cnt += 1
    return prime(cnt)


def scramble(s, array):
    lst = ['' for _ in range(len(s))]
    for i, j in enumerate(array):
        lst[j] = s[i] if i != j else '■'
    return ''.join(lst)


CONTEST02 = Event(
    'Contest 02',
    datetime(year=2023, month=12, day=8, hour=17, minute=10, second=0),
    [
        Task(
            id_='01-cats-and-mice',
            locator=FnLocator('cats_and_mice'),
            include=[],
            validator=DEFAULT_VAL,
            checker=EitherOf(SINGLE_STRING, SINGLE_NUMBER),
            tests=[
                ArgList("""\
            ..C......
            .........
            ....m...."""),
                ArgList("""\
            .C.......
            .........
            ......m.."""),
                ArgList("""\
            ..C......
            .........
            ........."""),
                *H.repeat_test(
                    R_INT(4, 20).map(
                        lambda x: CatsAndMiceGenerator(x)
                    ),
                    12
                )
            ],
            solution=cats_and_mice
        ),
        Task(
            id_='02-exchange',
            locator=FnLocator('exchange'),
            include=[],
            validator=DEFAULT_VAL,
            checker=EitherOf(SINGLE_STRING, SINGLE_NUMBER),
            tests=[
                ArgList([12, 34]),
                ArgList([55, 63]),
                ArgList([357, 579]),
                ArgList([1000000, 9999999]),
                ArgList([1000000, "bye"]),
                ArgList(["hello", 9999999]),
                ArgList(['hello', 'bye']),
                ArgList([1, 1]),
                ArgList([1, 0]),
                ArgList([0, 1]),
                *H.repeat_test(
                    ArgList(R_INT(100, 10 ** 9).repeat(2, as_type=list)),
                    10
                )
            ],
            solution=exchange
        ),
        Task(
            id_='03-sorting-cards',
            locator=FnLocator('sorting_cards'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_STRING),
            tests=[
                ArgList(['5', '4', 'T', 'Q', 'K', 'J', '6', '9', '3', '2', '7', 'A', '8']),
                ArgList(['Q', '2', '8', '6', 'J', 'K', '3', '9', '5', 'A', '4', '7', 'T']),
                ArgList(
                    ['5', '4', 'A', '2', 'A', '9', 'K', '7', '5', '8', '8', 'K', '4', '9', 'A', 'T', 'Q', '2', '6', 'A',
                     '2', 'K', '5', 'Q', 'A', '2', 'J', '8', '4', 'T', '4', '6', '8', '6', '5', '5', 'Q', '9', '4', 'A',
                     '7', 'Q', '4', '7', 'K', '4', 'Q', 'K', 'K', 'J', 'Q', '9', '6', '5', 'Q', '4', '8', '7', 'Q', '9',
                     '7', '2', 'J', 'Q', 'T', '2', '3', '4', '8', 'Q', '9', '7', 'K', 'T', 'J', '2', '3', '9']),
                *H.repeat_test(
                    ArgList(R_INT(1, 100).map(
                        lambda s: R_INT(0, 12).map(
                            lambda t: 'A23456789TJQK'[t]
                        ).repeat(s, as_type=list)
                    )),
                    12
                )
            ],
            solution=sorting_cards
        ),
        Task(
            id_='04-check-password',
            locator=FnLocator('check_password'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_STRING,
            tests=[
                ArgList(''),
                ArgList('password'),
                ArgList('P1@p'),
                ArgList('P1@pP1@p'),
                ArgList('P1@pP1@pP1@pP1@pP1@pP1@p'),
                ArgList('Paaaaaa222!!!'),
                *H.repeat_test(
                    ArgList(R_INT(7, 21).map(
                        lambda s: R_INT(35, 122).map(chr).repeat(s)
                    ).map(
                        lambda cs: ''.join(cs)
                    )),
                    19
                )
            ],
            solution=check_password
        ),
        Task(
            id_='05-sorted-people',
            locator=FnLocator('sorted_people'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_NUMBER),
            tests=[
                ArgList([-1, 150, 190, 170, -1, -1, 160, 180, -1]),
                ArgList([-1, -1, -1, -1, -1]),
                ArgList([4, 2, 9, 11, 2, 16]),
                *H.repeat_test(
                    ArgList(R_INT(1, 10000).map(
                        lambda s: R_INT(-1, 10 ** 6).repeat(s, as_type=list)
                    ).map(
                        lambda lst: [x for x in lst if x != 0]
                    )),
                    17
                )
            ],
            solution=sorted_people
        ),
        Task(
            id_='06-remove-doubles',
            locator=FnLocator('remove_doubles'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_STRING, as_type=tuple),
            tests=[
                ArgList('zzzzykkkd'),
                ArgList('abbbzz'),
                ArgList('xxbnnnnnyaaamaam'),
                ArgList('abbcccdddda'),
                ArgList('vvvvvoiiiiin'),
                ArgList('rrrmooomqqqqj'),
                ArgList('qqqqqqnpppgooooonpppppqmmmmmc'),
                ArgList('qqqqqwwwx'),
                ArgList('jjjfzzzzzzsddgrrrrru'),
                ArgList('jjjjjfuuuutgggggqppdaaas'),
                ArgList('iiiiibllllllyqqqqqbiiiiiituuf'),
                ArgList('mmmmmmuzzqllllmqqqp'),
                *H.repeat_test(
                    ArgList(R_INT(100, 1000).map(
                        lambda s: R_INT(ord('a'), ord('z')).map(chr).repeat(s)
                    ).map(
                        lambda cs: ''.join(cs)
                    )),
                    8
                )
            ],
            solution=remove_doubles
        ),
        Task(
            id_='07-close-primes',
            locator=FnLocator('close_primes'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_BOOL,
            tests=[
                ArgList(1, 3),
                ArgList(17, 19),
                ArgList(37, 47),
                ArgList(41, 99),
                ArgList(43, 47),
                ArgList(2, 3),
                ArgList(3, 4),
                ArgList(4, 6),
                ArgList(1000000007, 1000000009),
                ArgList(239, 240),
                ArgList(239, 241),
                ArgList(1, 4),
                ArgList(4, 5),
                ArgList(7, 9),
                ArgList(7, 7),
                ArgList(25, 25),
                ArgList(2, 5),
                ArgList(2, 7),
                ArgList(3, 7890),
                ArgList(3, 199),
                ArgList(3, 11)
            ],
            solution=close_primes
        ),
        Task(
            id_='08-scramble',
            locator=FnLocator('scramble'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_STRING,
            tests=[
                ArgList('abcd', [0, 3, 1, 2]),
                ArgList('sF351s', [5, 0, 3, 1, 4, 2]),
                ArgList('bak58', [2, 1, 4, 3, 0]),
                *H.repeat_test(
                    R_INT(1, 1000).map(
                        lambda s: ArgList(
                            R_INT(35, 122).map(chr).repeat(s).map(
                                lambda cs: ''.join(cs)
                            ),
                            R_PERM(s)
                        )
                    ),
                    12
                )
            ],
            solution=scramble
        )
    ]
)
