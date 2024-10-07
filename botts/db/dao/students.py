import time
from typing import Sequence

from ..ban import Ban
from ..student import Student
from ..tg_user import TGUser


class Students:
    @staticmethod
    def get_student_by_id(student_id: int) -> Student | None:
        query = (Student
                 .select(Student)
                 .where(Student.id_ == student_id))
        return query.first()

    @staticmethod
    def get_student_by_tg_id(tg_id: int) -> Student | None:
        query = (Student
                 .select(Student)
                 .join(TGUser)
                 .where(TGUser.tg_id == tg_id))
        return query.first()

    @staticmethod
    def get_students_starting_with(name_prefix: str) -> Sequence[Student]:
        query = (Student
                 .select()
                 .order_by(Student.name)
                 .where(Student.name.startswith(name_prefix)))
        return query.execute()

    @staticmethod
    def update_tg_data(student: Student, tg_id: int, username: str | None):
        query = (TGUser
                 .insert(student=student, tg_id=tg_id, username=username)
                 .on_conflict_replace())
        query.execute()

    @staticmethod
    def ban(student: Student, cause: str):
        query = (Ban
                 .insert(student=student, timestamp=time.time(), cause=cause))
        query.execute()


if __name__ == '__main__':
    student = Students.get_students_starting_with('Симончик')[0]
    Students.update_tg_data(student, 1, 'None')
