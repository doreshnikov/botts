import json
import math
from datetime import datetime
from typing import Any

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task
from botts.testsys.components.check.checker import BYTES, Checker, Result, SINGLE_NUMBER, Verdict
from botts.testsys.components.check.generator import ArgList, H, R_INT
from botts.testsys.components.check.validator import NO_EVAL, NO_EXEC, NO_IMPORTS
from botts.testsys.components.extract.jupyter import FnLocator
from botts.testsys.components.test.event import Event


def substitute_stdout(fn):
    import contextlib
    import io

    def wrapped(*args, **kwargs):
        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            fn(*args, **kwargs)
            return buffer.getvalue()

    return wrapped


def happy_new_year(n: int):
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


def sequence_element(n: int):
    return math.floor(math.sqrt(2 * n) + 0.5)


class FavouriteNumberChecker(Checker):
    def check(self, _: Any, out_data: Any, __: Any) -> Result:
        if type(out_data) not in (int, float, complex):
            return Result(Verdict.WA, f'expected a number, got {type(out_data)}')
        return Result(Verdict.OK, None)


def unix2dos_executor(fn):
    import uuid
    import pathlib
    import shutil

    class TmpDir:
        def __init__(self, path):
            self.path = pathlib.Path(path + str(uuid.uuid4()))

        def __enter__(self):
            self.path.mkdir(exist_ok=True)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            shutil.rmtree(self.path)

    def wrapped(data):
        tmp_dir = 'resources/tmp'
        with TmpDir(tmp_dir) as t:
            with open(t.path / 'inf', 'wb') as f:
                f.write(data)
            fn(str(t.path / 'inf'))
            with open(t.path / 'inf', 'rb') as f:
                res = f.read()
        return res

    return wrapped


def unix2dos(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    result = []
    for i, b in enumerate(data):
        result.append(b)
        if b == 10 and (i + 1 == len(data) or data[i + 1] != 13):
            result.append(13)

    with open(filename, 'wb') as f:
        f.write(bytes(result))


def json2yaml_executor(fn):
    import uuid
    import pathlib
    import shutil
    import json
    import yaml

    class TmpDir:
        def __init__(self, path):
            self.path = pathlib.Path(path + str(uuid.uuid4()))

        def __enter__(self):
            self.path.mkdir(exist_ok=True)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            shutil.rmtree(self.path)

    def wrapped(data):
        tmp_dir = 'resources/tmp'
        with TmpDir(tmp_dir) as t:
            with open(t.path / 'inf.json', 'w') as f:
                json.dump(data, f)
            result = fn(str(t.path / 'inf.json'))
            with open(t.path / 'inf.yaml', 'r') as f:
                output = yaml.safe_load(f)
        return result, output

    return wrapped


class Json2YamlChecker(Checker):
    def check(self, in_data: Any, out_data: Any, _: Any) -> Result:
        r1, r2 = out_data
        data = in_data.args[0]
        if data != r1:
            return Result(Verdict.WA, f'returned value {r1} doesn\'t match the input {data}')
        if data != r2:
            return Result(Verdict.WA, f'output {r2} doesn\'t match the input {data}')
        return Result(Verdict.OK, None)


def json2yaml(filename):
    import json
    import yaml

    with open(filename) as f:
        data = json.load(f)
    new_name = filename.removesuffix('.json') + '.yaml'
    with open(new_name, 'w') as f:
        yaml.dump(data, f)

    return data


def compress_executor(fn):
    import io

    class OpenDisabler:
        def __init__(self):
            self.open = open

        def __enter__(self):
            globals()['open'] = None
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            globals()['open'] = self.open

    encode, decode = fn()

    def wrapped(data, ignore=None):
        if ignore is not None:
            data = ignore

        with OpenDisabler():
            buffer = io.BytesIO()
            encode(data, buffer)
            code = buffer.getvalue()
            buffer.seek(0)
            result = decode(buffer)

        return result, len(code)

    return wrapped


class EncodeDecodeChecker(Checker):
    def check(self, in_data: Any, out_data: Any, answer: Any, **kwargs) -> Result:
        r_p, sz_p = out_data
        _, sz_a = answer
        data, grading = in_data.args[0], False
        if data == '_GRADING':
            data, grading = in_data.args[1], True
        if data != r_p:
            return Result(Verdict.WA, f'result {r_p} doesn\'t match the initial {data}')
        rate = sz_a / sz_p

        if grading:
            from botts.db import database

            cursor = database.execute_sql(
                'select * from compression_rate '
                'join student on student_id = student.id_ '
                'where student_id = ?', (kwargs['student_id'],)
            ).fetchall()
            if len(cursor) > 0:
                row = cursor[0]
                if row[1] < rate:
                    database.execute_sql(
                        'update compression_rate '
                        'set rate = ? '
                        'where student_id = ?', (rate, kwargs['student_id'])
                    )
            else:
                database.execute_sql(
                    'insert into compression_rate '
                    'values (?, ?)', (kwargs['student_id'], rate)
                )

        return Result(Verdict.OK, f'compression rate {sz_a / sz_p}')


def compress():
    import pickle

    return pickle.dump, pickle.load


with open('resources/tests/large-json.json', 'r') as f:
    LARGE_JSON = json.load(f)

HW03 = Event(
    'Homework 03',
    datetime(year=2024, month=1, day=15, hour=3, minute=0, second=0),
    [
        Task(
            id_='0-happy-new-year',
            locator=FnLocator('happy_new_year'),
            include=[],
            validator=NO_EXEC & NO_EVAL,
            checker=TreeChecker(),
            tests=[
                ArgList(i) for i in range(1, 30)
            ],
            solution=happy_new_year,
            executor=substitute_stdout,
            time_limit=10
        ),
        Task(
            id_='1-unix-to-dos',
            locator=FnLocator('unix2dos'),
            include=[
                inc('import os'),
                inc('os.makedirs(\'resources\', exist_ok=True)')
            ],
            validator=NO_IMPORTS & NO_EXEC & NO_EVAL,
            checker=BYTES,
            tests=[
                ArgList(b'Hello\n\rworld!\n\r'),
                ArgList(b'Hello\nworld!\n'),
                ArgList(b'Hello\n\rworld!\n'),
                ArgList(b'Hello\nworld!\n\r'),
                *H.repeat_test(
                    ArgList(R_INT(10, 20).repeat(100, as_type=list).map(bytes)),
                    6
                )
            ],
            solution=unix2dos,
            executor=unix2dos_executor
        ),
        Task(
            id_='2-json-to-yaml',
            locator=FnLocator('json2yaml'),
            include=[
                inc('import os'),
                inc('os.makedirs(\'resources\', exist_ok=True)')
            ],
            validator=NO_EXEC & NO_EVAL,
            checker=Json2YamlChecker(),
            tests=[
                ArgList({}),
                ArgList([]),
                ArgList([{}, {'x': []}, []]),
                ArgList({'a': 10, 'b': 20}),
                ArgList({'a': 10, 'b': [10, 20, 30, [40]]}),
                ArgList({'a': {'a': {'a': [1, 2, 3, 'x']}}}),
                ArgList({
                    "radio": {
                        "belt": [
                            720273602,
                            True,
                            True,
                            "energy",
                            "rubber",
                            "driven"
                        ],
                        "previous": 2006594047.118472,
                        "piano": -849323975.2636051,
                        "courage": "ability",
                        "ruler": True,
                        "several": "thou"
                    },
                    "she": False,
                    "voyage": "inch",
                    "afraid": 1544725653.698697,
                    "eventually": "daily",
                    "living": False
                }),
                ArgList([
                    {
                        "_id": "65a2968184f92a914506cae1",
                        "index": 0,
                        "guid": "00a9c032-6ead-44a7-8161-a82ca5f05acd",
                        "isActive": False,
                        "balance": "$1,124.40",
                        "picture": "http://placehold.it/32x32",
                        "age": 34,
                        "eyeColor": "blue",
                        "name": "Head Richardson",
                        "gender": "male",
                        "company": "REPETWIRE",
                        "email": "headrichardson@repetwire.com",
                        "phone": "+1 (865) 526-3747",
                        "address": "372 Matthews Court, Laurelton, North Dakota, 3432",
                        "about": "Do sunt labore qui veniam deserunt do. Ad tempor officia magna laboris adipisicing aliqua officia ipsum occaecat aute minim mollit amet non. Non consectetur excepteur elit consequat ut incididunt qui excepteur esse.\r\n",
                        "registered": "2022-11-17T01:48:27 -03:00",
                        "latitude": -19.135312,
                        "longitude": 90.566752,
                        "tags": [
                            "nulla",
                            "tempor",
                            "eiusmod",
                            "elit",
                            "sunt",
                            "sint",
                            "minim"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Burns Patton"
                            },
                            {
                                "id": 1,
                                "name": "Greer Bond"
                            },
                            {
                                "id": 2,
                                "name": "Medina Hess"
                            }
                        ],
                        "greeting": "Hello, Head Richardson! You have 1 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a296817be03232fffb70eb",
                        "index": 1,
                        "guid": "77aa1faa-9b9b-4e5f-ad94-7fbefbc81930",
                        "isActive": False,
                        "balance": "$1,831.49",
                        "picture": "http://placehold.it/32x32",
                        "age": 33,
                        "eyeColor": "green",
                        "name": "Horn Petersen",
                        "gender": "male",
                        "company": "OULU",
                        "email": "hornpetersen@oulu.com",
                        "phone": "+1 (971) 582-3977",
                        "address": "122 Cedar Street, Clay, Missouri, 2991",
                        "about": "Ipsum reprehenderit sunt magna esse ex enim consequat aliquip ut adipisicing. Voluptate in excepteur adipisicing ea. Nulla qui eu aliquip veniam eu ex cillum eiusmod excepteur dolore quis ipsum. Laborum tempor excepteur fugiat id ad minim elit consectetur cupidatat labore ut dolore esse commodo.\r\n",
                        "registered": "2015-01-27T12:04:57 -03:00",
                        "latitude": 10.323172,
                        "longitude": -70.254957,
                        "tags": [
                            "velit",
                            "dolor",
                            "sit",
                            "in",
                            "irure",
                            "reprehenderit",
                            "anim"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Maynard Price"
                            },
                            {
                                "id": 1,
                                "name": "Hazel Castaneda"
                            },
                            {
                                "id": 2,
                                "name": "Baldwin Lara"
                            }
                        ],
                        "greeting": "Hello, Horn Petersen! You have 5 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681400a4b7ccb2b95dd",
                        "index": 2,
                        "guid": "4cd6d54a-0678-472b-b736-21da645704d8",
                        "isActive": False,
                        "balance": "$3,993.98",
                        "picture": "http://placehold.it/32x32",
                        "age": 21,
                        "eyeColor": "blue",
                        "name": "Chasity Trevino",
                        "gender": "female",
                        "company": "UBERLUX",
                        "email": "chasitytrevino@uberlux.com",
                        "phone": "+1 (983) 489-2268",
                        "address": "856 Garnet Street, Nicholson, Guam, 1443",
                        "about": "Tempor ex eu nulla velit ullamco velit esse. Sunt elit exercitation ullamco in non anim quis esse culpa sint eiusmod eu velit. Consectetur quis consequat sunt irure eu consectetur Lorem irure culpa exercitation deserunt eiusmod reprehenderit labore. Elit eiusmod mollit ipsum qui commodo proident elit officia do nisi consectetur tempor cillum. Minim ut culpa proident reprehenderit cupidatat ex ipsum. Magna voluptate commodo irure esse sit fugiat adipisicing eiusmod labore ex dolor culpa eu.\r\n",
                        "registered": "2019-12-15T11:20:50 -03:00",
                        "latitude": 0.810423,
                        "longitude": -109.897694,
                        "tags": [
                            "aliqua",
                            "voluptate",
                            "sint",
                            "elit",
                            "deserunt",
                            "ad",
                            "fugiat"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Margo Coleman"
                            },
                            {
                                "id": 1,
                                "name": "Howe Campos"
                            },
                            {
                                "id": 2,
                                "name": "Cash Carter"
                            }
                        ],
                        "greeting": "Hello, Chasity Trevino! You have 6 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681f8d2c9b6dcf8e7c1",
                        "index": 3,
                        "guid": "539597c3-9582-4f43-8cb5-5975f744a8e7",
                        "isActive": True,
                        "balance": "$1,588.14",
                        "picture": "http://placehold.it/32x32",
                        "age": 36,
                        "eyeColor": "blue",
                        "name": "Vazquez Page",
                        "gender": "male",
                        "company": "TELEPARK",
                        "email": "vazquezpage@telepark.com",
                        "phone": "+1 (954) 466-2932",
                        "address": "385 Kane Street, Edinburg, Iowa, 5274",
                        "about": "Consequat duis voluptate esse officia elit cupidatat in. Consequat do mollit qui consectetur ea esse sint velit voluptate veniam mollit magna cupidatat. Ipsum consequat aliqua ut incididunt non anim nostrud reprehenderit occaecat culpa cupidatat est sint. Eu magna incididunt nisi aliqua irure aute mollit cupidatat et. Ad eiusmod aliquip ad id qui cillum. Consequat adipisicing aute esse aliquip nulla officia voluptate esse.\r\n",
                        "registered": "2023-10-26T05:01:15 -03:00",
                        "latitude": -83.307876,
                        "longitude": -32.402819,
                        "tags": [
                            "anim",
                            "occaecat",
                            "dolore",
                            "incididunt",
                            "eu",
                            "eiusmod",
                            "est"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Miriam Underwood"
                            },
                            {
                                "id": 1,
                                "name": "Rojas Schmidt"
                            },
                            {
                                "id": 2,
                                "name": "Robbie Britt"
                            }
                        ],
                        "greeting": "Hello, Vazquez Page! You have 1 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681c6241a77f6bea11a",
                        "index": 4,
                        "guid": "b8b94510-d26f-4611-a98a-b273ff6a0d9d",
                        "isActive": False,
                        "balance": "$2,847.94",
                        "picture": "http://placehold.it/32x32",
                        "age": 39,
                        "eyeColor": "blue",
                        "name": "Wheeler Cline",
                        "gender": "male",
                        "company": "ATGEN",
                        "email": "wheelercline@atgen.com",
                        "phone": "+1 (954) 589-3434",
                        "address": "200 Seagate Avenue, Limestone, Maryland, 1472",
                        "about": "Reprehenderit dolore qui minim ullamco eiusmod ea tempor deserunt. Mollit dolor eiusmod occaecat non laborum labore sint anim excepteur labore. Reprehenderit Lorem veniam amet sit quis aliquip magna incididunt. In sunt pariatur proident esse enim pariatur. Aliqua cupidatat incididunt esse do mollit Lorem deserunt velit laborum aliqua enim.\r\n",
                        "registered": "2018-10-11T07:19:16 -03:00",
                        "latitude": -12.299789,
                        "longitude": -122.655692,
                        "tags": [
                            "irure",
                            "elit",
                            "reprehenderit",
                            "ea",
                            "irure",
                            "nostrud",
                            "esse"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Cain Griffin"
                            },
                            {
                                "id": 1,
                                "name": "Leach Pace"
                            },
                            {
                                "id": 2,
                                "name": "Eugenia Acevedo"
                            }
                        ],
                        "greeting": "Hello, Wheeler Cline! You have 10 unread messages.",
                        "favoriteFruit": "apple"
                    },
                    {
                        "_id": "65a29681c77e08e92b5f0037",
                        "index": 5,
                        "guid": "1ccd4125-260d-4a42-bdb9-1068d6e1c141",
                        "isActive": True,
                        "balance": "$2,331.56",
                        "picture": "http://placehold.it/32x32",
                        "age": 39,
                        "eyeColor": "green",
                        "name": "Lester Higgins",
                        "gender": "male",
                        "company": "ENTOGROK",
                        "email": "lesterhiggins@entogrok.com",
                        "phone": "+1 (836) 485-3572",
                        "address": "744 Everit Street, Warsaw, North Carolina, 881",
                        "about": "Magna aliquip et ex ullamco dolor. Culpa do laboris voluptate pariatur fugiat fugiat consequat nisi. Commodo labore elit eiusmod in fugiat cupidatat adipisicing. In elit mollit ut non ea sit sint. Sunt aliquip occaecat elit est excepteur deserunt nisi nulla dolore ex do. Elit elit officia sunt eiusmod deserunt eu consequat ut duis sunt sit incididunt eu nisi.\r\n",
                        "registered": "2021-08-01T07:39:27 -03:00",
                        "latitude": 5.747329,
                        "longitude": 39.147798,
                        "tags": [
                            "tempor",
                            "dolor",
                            "et",
                            "occaecat",
                            "esse",
                            "consequat",
                            "ea"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Holt Alvarado"
                            },
                            {
                                "id": 1,
                                "name": "Kirsten Jordan"
                            },
                            {
                                "id": 2,
                                "name": "Willis Gordon"
                            }
                        ],
                        "greeting": "Hello, Lester Higgins! You have 6 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681054d64f120d9d454",
                        "index": 6,
                        "guid": "3590e037-ad3d-4fd0-803b-12298b940a00",
                        "isActive": True,
                        "balance": "$1,865.60",
                        "picture": "http://placehold.it/32x32",
                        "age": 32,
                        "eyeColor": "green",
                        "name": "Suzanne Warner",
                        "gender": "female",
                        "company": "DOGNOST",
                        "email": "suzannewarner@dognost.com",
                        "phone": "+1 (927) 582-2435",
                        "address": "143 Madison Street, Bedias, District Of Columbia, 3589",
                        "about": "In non laborum dolore enim veniam sint qui laborum adipisicing amet elit sit. Sint quis anim non ut aliqua non sit culpa ipsum veniam amet ullamco anim. Incididunt nulla reprehenderit dolore laborum sint pariatur proident. Reprehenderit excepteur do ea proident fugiat anim fugiat consequat cillum exercitation.\r\n",
                        "registered": "2019-11-04T07:44:14 -03:00",
                        "latitude": -39.791588,
                        "longitude": 24.346186,
                        "tags": [
                            "enim",
                            "quis",
                            "velit",
                            "do",
                            "consectetur",
                            "nulla",
                            "elit"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Neal Ramirez"
                            },
                            {
                                "id": 1,
                                "name": "Noreen Mercado"
                            },
                            {
                                "id": 2,
                                "name": "Mcgowan Hurst"
                            }
                        ],
                        "greeting": "Hello, Suzanne Warner! You have 7 unread messages.",
                        "favoriteFruit": "banana"
                    }
                ]),
                ArgList([
                    {
                        "accurate": "army",
                        "death": {
                            "teacher": "cream",
                            "wind": "curve",
                            "additional": 1651931656,
                            "although": True,
                            "solar": -814980532.0291977,
                            "funny": "temperature"
                        },
                        "check": -244017333.91869402,
                        "noon": True,
                        "degree": "customs",
                        "brother": -1865216199
                    },
                    True,
                    "well",
                    1472641469.0296402,
                    False,
                    "last"
                ])
            ],
            executor=json2yaml_executor,
            solution=json2yaml
        ),
        Task(
            id_='3-encode-decode',
            locator=FnLocator('compress'),
            include=[],
            validator=NO_EXEC & NO_EVAL,
            checker=EncodeDecodeChecker(),
            tests=[
                ArgList({}),
                ArgList([]),
                ArgList([{}, {'x': []}, []]),
                ArgList({'a': 10, 'b': 20}),
                ArgList({'a': 10, 'b': [10, 20, 30, [40]]}),
                ArgList({'a': {'a': {'a': [1, 2, 3, 'x']}}}),
                ArgList({
                    "radio": {
                        "belt": [
                            720273602,
                            True,
                            True,
                            "energy",
                            "rubber",
                            "driven"
                        ],
                        "previous": 2006594047.118472,
                        "piano": -849323975.2636051,
                        "courage": "ability",
                        "ruler": True,
                        "several": "thou"
                    },
                    "she": False,
                    "voyage": "inch",
                    "afraid": 1544725653.698697,
                    "eventually": "daily",
                    "living": False
                }),
                ArgList([
                    {
                        "_id": "65a2968184f92a914506cae1",
                        "index": 0,
                        "guid": "00a9c032-6ead-44a7-8161-a82ca5f05acd",
                        "isActive": False,
                        "balance": "$1,124.40",
                        "picture": "http://placehold.it/32x32",
                        "age": 34,
                        "eyeColor": "blue",
                        "name": "Head Richardson",
                        "gender": "male",
                        "company": "REPETWIRE",
                        "email": "headrichardson@repetwire.com",
                        "phone": "+1 (865) 526-3747",
                        "address": "372 Matthews Court, Laurelton, North Dakota, 3432",
                        "about": "Do sunt labore qui veniam deserunt do. Ad tempor officia magna laboris adipisicing aliqua officia ipsum occaecat aute minim mollit amet non. Non consectetur excepteur elit consequat ut incididunt qui excepteur esse.\r\n",
                        "registered": "2022-11-17T01:48:27 -03:00",
                        "latitude": -19.135312,
                        "longitude": 90.566752,
                        "tags": [
                            "nulla",
                            "tempor",
                            "eiusmod",
                            "elit",
                            "sunt",
                            "sint",
                            "minim"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Burns Patton"
                            },
                            {
                                "id": 1,
                                "name": "Greer Bond"
                            },
                            {
                                "id": 2,
                                "name": "Medina Hess"
                            }
                        ],
                        "greeting": "Hello, Head Richardson! You have 1 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a296817be03232fffb70eb",
                        "index": 1,
                        "guid": "77aa1faa-9b9b-4e5f-ad94-7fbefbc81930",
                        "isActive": False,
                        "balance": "$1,831.49",
                        "picture": "http://placehold.it/32x32",
                        "age": 33,
                        "eyeColor": "green",
                        "name": "Horn Petersen",
                        "gender": "male",
                        "company": "OULU",
                        "email": "hornpetersen@oulu.com",
                        "phone": "+1 (971) 582-3977",
                        "address": "122 Cedar Street, Clay, Missouri, 2991",
                        "about": "Ipsum reprehenderit sunt magna esse ex enim consequat aliquip ut adipisicing. Voluptate in excepteur adipisicing ea. Nulla qui eu aliquip veniam eu ex cillum eiusmod excepteur dolore quis ipsum. Laborum tempor excepteur fugiat id ad minim elit consectetur cupidatat labore ut dolore esse commodo.\r\n",
                        "registered": "2015-01-27T12:04:57 -03:00",
                        "latitude": 10.323172,
                        "longitude": -70.254957,
                        "tags": [
                            "velit",
                            "dolor",
                            "sit",
                            "in",
                            "irure",
                            "reprehenderit",
                            "anim"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Maynard Price"
                            },
                            {
                                "id": 1,
                                "name": "Hazel Castaneda"
                            },
                            {
                                "id": 2,
                                "name": "Baldwin Lara"
                            }
                        ],
                        "greeting": "Hello, Horn Petersen! You have 5 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681400a4b7ccb2b95dd",
                        "index": 2,
                        "guid": "4cd6d54a-0678-472b-b736-21da645704d8",
                        "isActive": False,
                        "balance": "$3,993.98",
                        "picture": "http://placehold.it/32x32",
                        "age": 21,
                        "eyeColor": "blue",
                        "name": "Chasity Trevino",
                        "gender": "female",
                        "company": "UBERLUX",
                        "email": "chasitytrevino@uberlux.com",
                        "phone": "+1 (983) 489-2268",
                        "address": "856 Garnet Street, Nicholson, Guam, 1443",
                        "about": "Tempor ex eu nulla velit ullamco velit esse. Sunt elit exercitation ullamco in non anim quis esse culpa sint eiusmod eu velit. Consectetur quis consequat sunt irure eu consectetur Lorem irure culpa exercitation deserunt eiusmod reprehenderit labore. Elit eiusmod mollit ipsum qui commodo proident elit officia do nisi consectetur tempor cillum. Minim ut culpa proident reprehenderit cupidatat ex ipsum. Magna voluptate commodo irure esse sit fugiat adipisicing eiusmod labore ex dolor culpa eu.\r\n",
                        "registered": "2019-12-15T11:20:50 -03:00",
                        "latitude": 0.810423,
                        "longitude": -109.897694,
                        "tags": [
                            "aliqua",
                            "voluptate",
                            "sint",
                            "elit",
                            "deserunt",
                            "ad",
                            "fugiat"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Margo Coleman"
                            },
                            {
                                "id": 1,
                                "name": "Howe Campos"
                            },
                            {
                                "id": 2,
                                "name": "Cash Carter"
                            }
                        ],
                        "greeting": "Hello, Chasity Trevino! You have 6 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681f8d2c9b6dcf8e7c1",
                        "index": 3,
                        "guid": "539597c3-9582-4f43-8cb5-5975f744a8e7",
                        "isActive": True,
                        "balance": "$1,588.14",
                        "picture": "http://placehold.it/32x32",
                        "age": 36,
                        "eyeColor": "blue",
                        "name": "Vazquez Page",
                        "gender": "male",
                        "company": "TELEPARK",
                        "email": "vazquezpage@telepark.com",
                        "phone": "+1 (954) 466-2932",
                        "address": "385 Kane Street, Edinburg, Iowa, 5274",
                        "about": "Consequat duis voluptate esse officia elit cupidatat in. Consequat do mollit qui consectetur ea esse sint velit voluptate veniam mollit magna cupidatat. Ipsum consequat aliqua ut incididunt non anim nostrud reprehenderit occaecat culpa cupidatat est sint. Eu magna incididunt nisi aliqua irure aute mollit cupidatat et. Ad eiusmod aliquip ad id qui cillum. Consequat adipisicing aute esse aliquip nulla officia voluptate esse.\r\n",
                        "registered": "2023-10-26T05:01:15 -03:00",
                        "latitude": -83.307876,
                        "longitude": -32.402819,
                        "tags": [
                            "anim",
                            "occaecat",
                            "dolore",
                            "incididunt",
                            "eu",
                            "eiusmod",
                            "est"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Miriam Underwood"
                            },
                            {
                                "id": 1,
                                "name": "Rojas Schmidt"
                            },
                            {
                                "id": 2,
                                "name": "Robbie Britt"
                            }
                        ],
                        "greeting": "Hello, Vazquez Page! You have 1 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681c6241a77f6bea11a",
                        "index": 4,
                        "guid": "b8b94510-d26f-4611-a98a-b273ff6a0d9d",
                        "isActive": False,
                        "balance": "$2,847.94",
                        "picture": "http://placehold.it/32x32",
                        "age": 39,
                        "eyeColor": "blue",
                        "name": "Wheeler Cline",
                        "gender": "male",
                        "company": "ATGEN",
                        "email": "wheelercline@atgen.com",
                        "phone": "+1 (954) 589-3434",
                        "address": "200 Seagate Avenue, Limestone, Maryland, 1472",
                        "about": "Reprehenderit dolore qui minim ullamco eiusmod ea tempor deserunt. Mollit dolor eiusmod occaecat non laborum labore sint anim excepteur labore. Reprehenderit Lorem veniam amet sit quis aliquip magna incididunt. In sunt pariatur proident esse enim pariatur. Aliqua cupidatat incididunt esse do mollit Lorem deserunt velit laborum aliqua enim.\r\n",
                        "registered": "2018-10-11T07:19:16 -03:00",
                        "latitude": -12.299789,
                        "longitude": -122.655692,
                        "tags": [
                            "irure",
                            "elit",
                            "reprehenderit",
                            "ea",
                            "irure",
                            "nostrud",
                            "esse"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Cain Griffin"
                            },
                            {
                                "id": 1,
                                "name": "Leach Pace"
                            },
                            {
                                "id": 2,
                                "name": "Eugenia Acevedo"
                            }
                        ],
                        "greeting": "Hello, Wheeler Cline! You have 10 unread messages.",
                        "favoriteFruit": "apple"
                    },
                    {
                        "_id": "65a29681c77e08e92b5f0037",
                        "index": 5,
                        "guid": "1ccd4125-260d-4a42-bdb9-1068d6e1c141",
                        "isActive": True,
                        "balance": "$2,331.56",
                        "picture": "http://placehold.it/32x32",
                        "age": 39,
                        "eyeColor": "green",
                        "name": "Lester Higgins",
                        "gender": "male",
                        "company": "ENTOGROK",
                        "email": "lesterhiggins@entogrok.com",
                        "phone": "+1 (836) 485-3572",
                        "address": "744 Everit Street, Warsaw, North Carolina, 881",
                        "about": "Magna aliquip et ex ullamco dolor. Culpa do laboris voluptate pariatur fugiat fugiat consequat nisi. Commodo labore elit eiusmod in fugiat cupidatat adipisicing. In elit mollit ut non ea sit sint. Sunt aliquip occaecat elit est excepteur deserunt nisi nulla dolore ex do. Elit elit officia sunt eiusmod deserunt eu consequat ut duis sunt sit incididunt eu nisi.\r\n",
                        "registered": "2021-08-01T07:39:27 -03:00",
                        "latitude": 5.747329,
                        "longitude": 39.147798,
                        "tags": [
                            "tempor",
                            "dolor",
                            "et",
                            "occaecat",
                            "esse",
                            "consequat",
                            "ea"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Holt Alvarado"
                            },
                            {
                                "id": 1,
                                "name": "Kirsten Jordan"
                            },
                            {
                                "id": 2,
                                "name": "Willis Gordon"
                            }
                        ],
                        "greeting": "Hello, Lester Higgins! You have 6 unread messages.",
                        "favoriteFruit": "banana"
                    },
                    {
                        "_id": "65a29681054d64f120d9d454",
                        "index": 6,
                        "guid": "3590e037-ad3d-4fd0-803b-12298b940a00",
                        "isActive": True,
                        "balance": "$1,865.60",
                        "picture": "http://placehold.it/32x32",
                        "age": 32,
                        "eyeColor": "green",
                        "name": "Suzanne Warner",
                        "gender": "female",
                        "company": "DOGNOST",
                        "email": "suzannewarner@dognost.com",
                        "phone": "+1 (927) 582-2435",
                        "address": "143 Madison Street, Bedias, District Of Columbia, 3589",
                        "about": "In non laborum dolore enim veniam sint qui laborum adipisicing amet elit sit. Sint quis anim non ut aliqua non sit culpa ipsum veniam amet ullamco anim. Incididunt nulla reprehenderit dolore laborum sint pariatur proident. Reprehenderit excepteur do ea proident fugiat anim fugiat consequat cillum exercitation.\r\n",
                        "registered": "2019-11-04T07:44:14 -03:00",
                        "latitude": -39.791588,
                        "longitude": 24.346186,
                        "tags": [
                            "enim",
                            "quis",
                            "velit",
                            "do",
                            "consectetur",
                            "nulla",
                            "elit"
                        ],
                        "friends": [
                            {
                                "id": 0,
                                "name": "Neal Ramirez"
                            },
                            {
                                "id": 1,
                                "name": "Noreen Mercado"
                            },
                            {
                                "id": 2,
                                "name": "Mcgowan Hurst"
                            }
                        ],
                        "greeting": "Hello, Suzanne Warner! You have 7 unread messages.",
                        "favoriteFruit": "banana"
                    }
                ]),
                ArgList([
                    {
                        "accurate": "army",
                        "death": {
                            "teacher": "cream",
                            "wind": "curve",
                            "additional": 1651931656,
                            "although": True,
                            "solar": -814980532.0291977,
                            "funny": "temperature"
                        },
                        "check": -244017333.91869402,
                        "noon": True,
                        "degree": "customs",
                        "brother": -1865216199
                    },
                    True,
                    "well",
                    1472641469.0296402,
                    False,
                    "last"
                ]),
                ArgList('_GRADING', LARGE_JSON)
            ],
            executor=compress_executor,
            solution=compress,
            extended_info=True,
            time_limit=10
        ),
        Task(
            id_='4-sequence-element',
            locator=FnLocator('sequence_element'),
            include=[],
            validator=NO_EXEC & NO_EVAL,
            checker=SINGLE_NUMBER,
            tests=[
                      ArgList(i) for i in range(1, 80)
                  ] + list(map(ArgList, [2023, 2024, 100000, 1000000000, 1000000007, 2237768762])),
            solution=sequence_element
        ),
        Task(
            id_='5-favourite-number',
            locator=FnLocator('favourite_number'),
            include=[],
            validator=NO_EXEC & NO_EVAL,
            tests=[ArgList()],
            checker=FavouriteNumberChecker(),
            solution=lambda: 0
        )
    ]
)
