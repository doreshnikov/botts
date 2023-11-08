from peewee import CharField, ForeignKeyField, IntegerField, Model

from . import database
from .student import Student


class TGUser(Model):
    student = ForeignKeyField(
        Student, backref='tg_user', field='id_',
        primary_key=True, lazy_load=False
    )
    tg_id = IntegerField(index=True, unique=True)
    username = CharField(index=True, unique=True, null=True)

    class Meta:
        database = database
        table_name = 'tg_user'


database.create_tables([TGUser], safe=True)
