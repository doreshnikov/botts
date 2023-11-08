import random

from migrate import course_table
from db import User

ALPHA = list(map(chr, range(ord('a'), ord('z') + 1)))

count = len(course_table)
id_length = len(str(count))
usernames = [f'{i:0{id_length}d}' for i in range(count)]


def gen_password(n: int, seed) -> str:
    random.seed(seed)
    s = [random.choice(ALPHA) for _ in range(n)]
    return ''.join(s)


def populate():
    for row, username in zip(course_table.iterrows(), usernames):
        _, row = row
        User.insert({
            User.student_name: row['Имя'],
            User.direction: row['Направление'],
            User.group: row['Текущая группа'],
            User.cf_username: f'student-{username}',
            User.cf_password: gen_password(10, username + 'ummm salty@$...')
        }).execute()


def load():
    rows = User.select().order_by(User.id_).dicts()
    with open('cf_setup.txt', 'w', encoding='utf8') as cf_setup_file:
        for row in rows:
            print(
                f' | {row["cf_username"]} | {row["cf_password"]} | {row["student_name"]}',
                file=cf_setup_file
            )


if __name__ == '__main__':
    load()