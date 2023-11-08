from peewee import AutoField, CharField, ForeignKeyField, Model, TimestampField

from . import database
from .student import Student


class Ban(Model):
    id_ = AutoField(primary_key=True)
    timestamp = TimestampField()
    cause = CharField()
    student = ForeignKeyField(
        Student, backref='bans', field='id_',
        lazy_load=False
    )

    class Meta:
        database = database
        table_name = 'ban'


database.create_tables([Ban], safe=True)
