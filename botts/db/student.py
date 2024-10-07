from peewee import AutoField, CharField, Model

from . import database


class Student(Model):
    id_ = AutoField(primary_key=True)
    name = CharField(index=True, unique=False)
    speciality = CharField()
    group = CharField(null=True)

    class Meta:
        database = database
        indexes = (
            (('name', 'speciality'), True),
            (('name', 'group'), True),
        )
        table_name = 'student'


database.create_tables([Student], safe=True)
