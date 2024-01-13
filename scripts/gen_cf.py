import pandas
from peewee import SqliteDatabase

database = SqliteDatabase(
    '../data.db',
    pragmas={
        'journal_mode': 'wal',
        'foreign_keys': 1,
        'ignore_check_constrains': 0,
    },
)
database.connect()

users = pandas.read_csv('group-02', sep='\t')

if __name__ == '__main__':
    for i, user in users.iterrows():
        if i < 3:
            continue
        print(user['Имя'], flush=True)
        database.execute_sql(
            '''
            INSERT INTO student ("name", "speciality", "group") VALUES 
            (?, ?, ?);
            ''',
            (user['Имя'],
             user['Направление'],
             user['Текущая группа'])
        )
