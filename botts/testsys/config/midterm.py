from sys import setrecursionlimit
from datetime import datetime

from ..components.base.include import inc
from ..components.base.task import Task
from ..components.check.checker import DictOf, EitherOf, SequenceOf, SINGLE_BOOL, SINGLE_FLOAT_6, \
    SINGLE_NUMBER, \
    SINGLE_STRING
from ..components.check.generator import ArgList, H, R_INT, R_STRING
from ..components.check.validator import NO_EVAL, NO_EXEC, NO_IMPORTS, NoFnCall, NoNameNode
from ..components.extract.jupyter import FnLocator
from ..components.test.event import Event

DEFAULT_VAL = NO_IMPORTS & NO_EXEC & NO_EVAL & NoNameNode('globals')

setrecursionlimit(100000)


def books(lst):
    authors = {}
    for i in lst:
        if i[0] not in authors.keys():
            authors[i[0]] = []
        authors[i[0]].append(i[1])
    return authors


def count_letters(text):
    def calculate_frequency(letter_count):
        total_letters = sum(letter_count.values())
        letter_frequency = {}
        for current_letter, count in letter_count.items():
            letter_frequency[current_letter] = count / total_letters
        return letter_frequency

    lower_text = text.lower()
    letter_count = {}
    for char in lower_text:
        if char.isalpha():
            if char in letter_count:
                letter_count[char] += 1
            else:
                letter_count[char] = 1
    return calculate_frequency(letter_count)


def abundant(x):
    l = 0
    for i in range(1, x):
        if x % i == 0:
            l += i
    return abundant(x - 1) if l < x else [x, l - x]


def decimal(num):
    s = str(num)
    d = 0
    for i, num in enumerate(s[::-1]):
        if num == '1':
            d += 2 ** i
    return d


def students(first, second):
    f = set(first.split(', '))
    s = set(second.split(', '))
    students = list(f.intersection(s))
    num = len(f.symmetric_difference(s))
    return students, num


def powers(x):
    return x > 2 and x.bit_count() <= 3


def sum_numbers(lst):
    if lst and lst[0] + lst[-1] != sum(lst[1:-1]):
        return sum_numbers(lst[1:-1])
    return lst


def one_true(*args):
    return args.count(True) == 1


def polydivisible(x):
    return True if x < 10 else False if x % len(str(x)) != 0 else polydivisible(x // 10)


def calculate(s):
    import re
    n = [int(i) for i in re.findall(r'\d+', s)]
    return sum(n) if 'took' in s else n[0] - n[1]


def alphabet_words(s):
    data = list(set(s.split()))
    data.sort()
    return data


def entrance(office):
    if '.' in office[0]:
        return office[0].index('.'), 0
    elif '.' in office[-1]:
        return office[-1].index('.'), len(office) - 1
    else:
        for i, row in enumerate(office):
            if '.' == row[0]:
                return 0, i
            elif '.' == row[-1]:
                return len(row) - 1, i
            elif ' .' in row:
                return row.index('.'), i
            elif '. ' in row:
                return len(row) - 1 - row[::-1].index('.'), i
            elif '#.#' in row and row.count('.') > 1:
                return len(row) - 1 - row[::-1].find('#.#') - 1, i


def projection_area(grid):
    xy = sum(i > 0 for s in grid for i in s)
    xz = sum(max(s) for s in grid)
    yz = sum(max(s[i] for s in grid) for i in range(len(grid)))
    return xy + xz + yz


MIDTERM = Event(
    'Midterm',
    datetime(year=2023, month=11, day=10, hour=14, minute=5, second=0),
    [
        Task(
            id_='01-books',
            locator=FnLocator('books'),
            include=[],
            validator=DEFAULT_VAL,
            checker=DictOf(SINGLE_STRING, SequenceOf(SINGLE_STRING, sorted=True)),
            tests=[
                ArgList(
                    [('Джейн Остин', 'Эмма'), ('Джейн Остин', 'Гордость и предубеждение'), ('Джордж Оруэлл', '1984'),
                     ('Джейн Остин', 'Доводы рассудка'), ('Джордж Оруэлл', 'Скотный двор'),
                     ('Лев Толстой', 'Анна Каренина')]
                ),
                ArgList([]),
                *H.repeat_test(
                    R_STRING(2, 'a', 'z').repeat(100, as_type=list).map(
                        lambda names: R_STRING(10, 'a', 'z').repeat(100, as_type=list).map(
                            lambda titles: ArgList(list(zip(names, titles)))
                        )
                    ),
                    number=13
                )
            ],
            solution=books
        ),
        Task(
            id_='02-count-letters',
            locator=FnLocator('count_letters'),
            include=[],
            validator=DEFAULT_VAL,
            checker=DictOf(SINGLE_STRING, SINGLE_FLOAT_6),
            tests=[
                ArgList('У лукоморья дуб зелёный;'),
                ArgList("""
                    У лукоморья дуб зелёный;
                    Златая цепь на дубе том:
                    И днём и ночью кот учёный
                    Всё ходит по цепи кругом;
                    Идёт направо — песнь заводит,
                    Налево — сказку говорит.
                    Там чудеса: там леший бродит,
                    Русалка на ветвях сидит;
                    Там на неведомых дорожках
                    Следы невиданных зверей;
                    Избушка там на курьих ножках
                    Стоит без окон, без дверей;
                    Там лес и дол видений полны;
                    Там о заре прихлынут волны
                    На брег песчаный и пустой,
                    И тридцать витязей прекрасных
                    Чредой из вод выходят ясных,
                    И с ними дядька их морской;
                    Там королевич мимоходом
                    Пленяет грозного царя;
                    Там в облаках перед народом
                    Через леса, через моря
                    Колдун несёт богатыря;
                    В темнице там царевна тужит,
                    А бурый волк ей верно служит;
                    Там ступа с Бабою Ягой
                    Идёт, бредёт сама собой,
                    Там царь Кащей над златом чахнет;
                    Там русский дух… там Русью пахнет!
                    И там я был, и мёд я пил;
                    У моря видел дуб зелёный;
                    Под ним сидел, и кот учёный
                    Свои мне сказки говорил.
                """),
                ArgList('Count letters do count really please'),
                ArgList(''),
                ArgList('punc!u&ti0n is 1mp0r!ant?'),
                *H.repeat_test(
                    ArgList(R_STRING(1000, '!', ']')),
                    number=10
                )
            ],
            solution=count_letters
        ),
        Task(
            id_='03-abundant',
            locator=FnLocator('abundant'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_NUMBER),
            tests=[
                ArgList(19),
                ArgList(100),
                ArgList(999),
                *H.repeat_test(
                    ArgList(R_INT(1, 1000)),
                    number=12
                )
            ],
            solution=abundant
        ),
        Task(
            id_='04-decimal',
            locator=FnLocator('decimal'),
            include=[],
            validator=DEFAULT_VAL & NoFnCall('int') & NoNameNode('int'),
            checker=SINGLE_NUMBER,
            tests=[
                ArgList(100),
                ArgList(1001000),
                ArgList(100111111),
                ArgList(0),
                *H.repeat_test(
                    R_INT(0, 1 << 100).map(
                        lambda x: ArgList(int(bin(x)[2:]))
                    ),
                    number=11
                )
            ],
            solution=decimal
        ),
        Task(
            id_='05-students',
            locator=FnLocator('students'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(EitherOf(SequenceOf(SINGLE_STRING, sorted=True), SINGLE_NUMBER), as_type=tuple),
            tests=[
                ArgList('Иванов, Петров, Сидоров, Иванова, Александров, Орешников',
                        'Орешников, Сидоров, Петрова, Смирнова'),
                ArgList('Иванов', 'Иванов'),
                ArgList('Иванов', ''),
                ArgList('', ''),
                *H.repeat_test(
                    R_STRING(10, 'a', 'k').repeat(100, as_type=list).map(
                        lambda x: R_STRING(10, 'a', 'k').repeat(100, as_type=list).map(
                            lambda y: ArgList(', '.join(x), ', '.join(y))
                        )
                    ),
                    number=11
                )
            ],
            solution=students
        ),
        Task(
            id_='06-powers',
            locator=FnLocator('powers'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_BOOL,
            tests=[
                ArgList(1),
                ArgList(2),
                ArgList(3),
                ArgList(5),
                ArgList(15),
                *H.repeat_test(
                    R_INT(0, 100).repeat(3).map(
                        lambda ds: R_INT(0, 1).map(
                            lambda flag: ArgList(
                                (R_INT(0, 1 << 100) if flag else R_INT(0, 0)).map(
                                    lambda x: x ^ (1 << ds[0]) ^ (1 << ds[1]) ^ (1 << ds[2])
                                )
                            )
                        )
                    ),
                    number=10
                )
            ],
            solution=powers
        ),
        Task(
            id_='07-sum-numbers',
            locator=FnLocator('sum_numbers'),
            include=[
                inc('from sys import setrecursionlimit'),
                inc('setrecursionlimit(100000)')
            ],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_NUMBER),
            tests=[
                ArgList([1, 2, 3, 4, 5]),
                ArgList([1, -1]),
                ArgList([100, 0, -100]),
                *H.repeat_test(
                    R_INT(-1000, 1000).map(
                        lambda x: R_INT(0, 1).map(
                            lambda flag: R_INT(-10000, 10000).repeat(1000, as_type=list).map(
                                lambda add1: R_INT(-10000, 10000).repeat(1000, as_type=list).map(
                                    lambda add2: ArgList(
                                        add2[:500] + add1 + [x, x] + [2 * x * (i + 1) - v for i, v in
                                                                      enumerate(add1[::-1])] + add2[500:]
                                        if flag
                                        else add2[:500] + add1 + [x] + [x * (1 + 2 * i) - v for i, v in
                                                                        enumerate(add1[::-1])] + add2[500:]
                                    )
                                )
                            )
                        )
                    ),
                    number=12
                )
            ],
            solution=sum_numbers
        ),
        Task(
            id_='08-one-true',
            locator=FnLocator('one_true'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_BOOL,
            tests=[
                ArgList(),
                ArgList(True, False, False),
                ArgList(True, False, False, True),
                ArgList(False, False, False, False),
                *H.repeat_test(
                    R_INT(1, 100).map(
                        lambda x: R_INT(0, 1).repeat(x).map(
                            lambda a: ArgList(list(map(bool, a)))
                        )
                    ),
                    number=11
                )
            ],
            solution=one_true
        ),
        Task(
            id_='09-polydivisible',
            locator=FnLocator('polydivisible'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_BOOL,
            tests=[
                ArgList(0),
                ArgList(1),
                ArgList(1020005),
                ArgList(1073741823),
                *H.repeat_test(
                    ArgList(R_INT(0, 1 << 100)),
                    number=11
                )
            ],
            solution=polydivisible
        ),
        Task(
            id_='10-calculate',
            locator=FnLocator('calculate'),
            include=[
                inc('import re')
            ],
            validator=DEFAULT_VAL,
            checker=SINGLE_NUMBER,
            tests=[
                ArgList('The monkey has 10 apples and gave 3'),
                ArgList('The cat has 13 oranges and took 6'),
                ArgList('Kangaroo has 254 bananas and gave 1'),
                *H.repeat_test(
                    R_INT(0, 1 << 100).map(
                        lambda x: R_INT(0, 1 << 100).map(
                            lambda y: R_INT(0, 1).map(
                                lambda flag: ArgList(
                                    f'Absolute being resided in the tower and held {max(x, y)} power\n'
                                    f'But then he {"took" if flag else "gave"} {min(x, y)} and died'
                                )
                            )
                        )
                    ),
                    number=12
                )
            ],
            solution=calculate
        ),
        Task(
            id_='11-alphabet-words',
            locator=FnLocator('alphabet_words'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_STRING),
            tests=[
                ArgList('банан букашка жук банан яблоко лев лев жуки капкан'),
                ArgList(''),
                ArgList('x x x x'),
                ArgList('н о пр сту фхцч шщъыь абвгд еёжз ийк лм'),
                *H.repeat_test(
                    R_STRING(100, 'a', 'z').repeat(100, as_type=list).map(
                        lambda words: ArgList(' '.join(words))
                    ),
                    number=11
                )
            ],
            solution=alphabet_words
        ),
        Task(
            id_='12-entrance',
            locator=FnLocator('entrance'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SequenceOf(SINGLE_NUMBER, as_type=tuple),
            tests=[
                ArgList(['#######',
                         '#.....#',
                         '#.#.###',
                         '#.#',
                         '###']),
                ArgList([' #####',
                         ' #...#',
                         ' ....#',
                         ' #...#',
                         '##...#',
                         '#....#',
                         '######'])
            ],
            solution=entrance
        ),
        Task(
            id_='13-projection-area',
            locator=FnLocator('projection_area'),
            include=[],
            validator=DEFAULT_VAL,
            checker=SINGLE_NUMBER,
            tests=[
                ArgList([[2]]),
                ArgList([[1, 0], [0, 2]]),
                ArgList([[1, 0], [2, 0]]),
                *H.repeat_test(
                    R_INT(1, 100).repeat(2).map(
                        lambda sz: ArgList(R_INT(0, 20).repeat(sz[0], as_type=list).repeat(sz[1], as_type=list))
                    ),
                    number=12
                )
            ],
            solution=projection_area
        )
    ]
)
