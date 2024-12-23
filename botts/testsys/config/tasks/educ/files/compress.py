import textwrap
import json
from typing import Any

from botts.testsys.components.base.include import inc
from botts.testsys.components.base.task import Task, Statement
from botts.testsys.components.check.checker import Checker, Result, Verdict
from botts.testsys.components.check.generator import ArgList
from botts.testsys.components.check.validator import NO_IMPORTS, NO_EXEC, NO_EVAL
from botts.testsys.components.extract.jupyter import FnLocator


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


from botts.db import database
from botts.db.student import Student
from peewee import AutoField, ForeignKeyField, FloatField, Model

class CRTable(Model):
    id_ = AutoField(primary_key=True)
    student = ForeignKeyField(Student, field='id_', lazy_load=False)
    rate = FloatField()
    
    class Meta:
        database = database
        table_name = '__task_compression_rate'

database.create_tables([CRTable], safe=True)


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
            cursor = database.execute_sql(
                'select * from __task_compression_rate '
                'join student on student_id = student.id_ '
                'where student_id = ?', (kwargs['student_id'],)
            ).fetchall()
            if len(cursor) > 0:
                row = cursor[0]
                if row[1] < rate:
                    database.execute_sql(
                        'update __task_compression_rate '
                        'set rate = ? '
                        'where student_id = ?', (rate, kwargs['student_id'])
                    )
            else:
                database.execute_sql(
                    'insert into __task_compression_rate '
                    'values (?, ?)', (kwargs['student_id'], rate)
                )

        return Result(Verdict.OK, f'compression rate {sz_a / sz_p}')


def solution():
    import pickle

    return pickle.dump, pickle.load


with open('resources/tests/fixtures/large-json.json', 'r') as f:
    LARGE_JSON = json.load(f)



TASK = Task(
    id_='encode-decode',
    statement=Statement(
        md=textwrap.dedent('''
        `> COMPRESS [бонусное задание]`
        
        Напишите функцию `compress()`, не принимающую аргументов и возвращающую 
        две другие функции.
        
        Первая из возвращаемых функций должна принимать на вход данные (`json`-like объект, 
        словарь с полями – такими же словарями или массивами) и файл, открытый на запись 
        (то, что возвращает `open`), и должна записывать эти данные в данный файл в любом виде.
        
        Вторая функция должна принимать только файл, открытый на чтение, в который что-то было 
        записано с помощью первой функции, и возвращать записанные в нем данные (такой же `json`-like объект).
        
        **Внимание**: вы не обязаны записывать текст в том же виде, в котором он вам дается. 
        Ваша задача – записать и прочитать текст в максимально сжатом компактном виде. 
        Задание будет засчитано, если ваша функция проходит следующую проверку:
        ```py
        encode, decode = compress()
        s = {'a': 1, 'b': [2, {'c': 'd'}]}
        with open('какой-то файл.txt', 'wb') as f:
            encode(s, f)
        with open('какой-то файл.txt', 'rb') as f:
            s_new = decode(f)
        # s должен совпадать с s_new
        ```
        Но чем меньше будет размер файла после вызова `encode`, тем больше баллов вы получите.
        
        **В этом задании разрешено использовать импорты**, но постарайтесь не сломать систему.
        ''')
    ),
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
    solution=solution,
    extended_info=True,
    time_limit=10
)
