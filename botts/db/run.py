from peewee import AutoField, CharField, ForeignKeyField, IntegerField, Model

from . import database
from .submission import Submission


class Run(Model):
    id_ = AutoField(primary_key=True)
    task_id = CharField()
    solution_source = CharField()
    solution_hash = CharField()
    verdict = CharField()
    comment = CharField(null=True)
    invoker_port = IntegerField()
    invoker_id = CharField()
    submission = ForeignKeyField(
        Submission, backref='runs', field='id_',
        lazy_load=False
    )

    class Meta:
        database = database
        indexes = (
            (('submission_id', 'task_id'), True),
        )
        table_name = 'run'


database.create_tables([Run], safe=True)
