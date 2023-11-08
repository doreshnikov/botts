from peewee import AutoField, CharField, ForeignKeyField, IntegerField, Model, TimestampField

from . import database
from .student import Student


class Submission(Model):
    id_ = AutoField(primary_key=True)
    timestamp = TimestampField()
    event = CharField()
    file_path = CharField()
    message_id = IntegerField()
    student = ForeignKeyField(
        Student, backref='submissions', field='id_',
        lazy_load=False
    )

    class Meta:
        database = database
        table_name = 'submission'


database.create_tables([Submission], safe=True)
