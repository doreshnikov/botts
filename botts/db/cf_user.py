from peewee import CharField, ForeignKeyField, Model

from . import database
from .student import Student


class CFUser(Model):
    student = ForeignKeyField(
        Student, backref='cf_user', field='id_',
        primary_key=True, lazy_load=False
    )
    username = CharField(index=True, unique=True)
    password = CharField()

    class Meta:
        database = database
        table_name = 'cf_user'


database.create_tables([CFUser], safe=True)
