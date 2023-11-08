from peewee import SqliteDatabase

database = SqliteDatabase(
    'data.db',
    pragmas={
        'journal_mode': 'wal',
        'foreign_keys': 1,
        'ignore_check_constrains': 0,
    },
)
database.connect()
