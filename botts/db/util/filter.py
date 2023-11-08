import operator
from dataclasses import dataclass
from typing import Any, Sequence

from peewee import AutoField, CharField, Expression, Field, ForeignKeyField, IntegerField, Model

from botts.db.run import Run
from botts.db.student import Student
from botts.db.submission import Submission


@dataclass
class DBFilter:
    _types_mapping = {
        AutoField.field_type: int,
        IntegerField.field_type: int,
        ForeignKeyField.field_type: int,
        CharField.field_type: str
    }
    _op_mapping = {
        '=': operator.eq,
        '>': operator.gt,
        '<': operator.lt,
        '@': lambda x, y: x.in_(y),
        '~': lambda x, y: x.like_(y)
    }
    _tables = [
        Student,
        Submission,
        Run
    ]

    model: str
    field: str
    op: str
    value: Any

    @property
    def _accepts_sequence(self):
        return self.op in ['in']

    def to_orm(self, model: type(Model)) -> Expression:
        field_name = self.field
        if not hasattr(model, self.field):
            field_name += '_'
        field: Field = getattr(model, field_name)
        field_type = field.field_type
        python_type = DBFilter._types_mapping.get(field_type)

        if not python_type:
            raise TypeError(f'filters for type \'{field_type}\' are not supported')
        if not self._accepts_sequence and not isinstance(self.value, python_type):
            try:
                self.value = python_type(self.value)
            except ValueError | TypeError:
                raise TypeError(f'invalid value {repr(self.value)} for type \'{field_type}\'')
        if self._accepts_sequence:
            if not isinstance(self.value, Sequence):
                raise TypeError(f'invalid value {repr(self.value)} for operator \'{self.op}\')')
            if len(self.value) > 0 and not isinstance(self.value[0], python_type):
                try:
                    self.value = [python_type(sub_value) for sub_value in self.value]
                except ValueError | TypeError:
                    raise TypeError(f'invalid value {repr(self.value[0])} for type \'{field_type}\'')
        if self.op not in DBFilter._op_mapping:
            raise TypeError(f'unsupported filter operator \'{self.op}\'')

        return DBFilter._op_mapping[self.op](field, self.value)

    def _get_model(self):
        for model in DBFilter._tables:
            if model.__name__.lower() == self.model.lower():
                return model

    @staticmethod
    def join_filters(filters: Sequence['DBFilter']):
        where_clause = None
        for filter_ in filters:
            model = filter_._get_model()
            if model is None:
                continue
            if where_clause is None:
                where_clause = filter_.to_orm(model)
                continue
            where_clause &= filter_.to_orm(model)
        return where_clause

    @staticmethod
    def parse(s: str, safe: bool = True):
        # TODO make safer
        items = s.split(' ')
        model, field = items[0].split('.')
        if items[2].startswith("'") and items[2].endswith("'"):
            items[2] = items[2][1:-1]
        filter_ = DBFilter(model, field, items[1], items[2])
        if filter_._get_model() is None:
            return None
        return filter_

    def __str__(self):
        return f'{self.model}.{self.field} {self.op} {repr(self.value)}'
