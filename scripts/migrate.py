import pandas as pd

from db.student import Student
from db.cf_user import CFUser
from db.tg_user import TGUser

with open('students.tsv', encoding='utf8') as students_file:
    table = pd.read_csv(students_file, sep='\t')

table.drop(table.index[[0, 1, 2]], inplace=True)
table.reset_index(inplace=True, drop=True)


# def populate():
#     for _, row in table.iterrows():
#         student = Student.create(
#             name=row['Имя'],
#             speciality=row['Направление'],
#             group=row['Текущая группа']
#         )
#         if user := User.get_or_none(User.student_name == student.name):
#             CFUser.create(
#                 student=student,
#                 username=user.cf_username,
#                 password=user.cf_password
#             )
#         else:
#             print(f'Not found: {student.name}')


# def migrate_tg_data():
#     for _, row in table.iterrows():
#         student = Student.get(Student.name == row['Имя'])
#         if user := User.get_or_none(User.student_name == student.name):
#             if user.tg_id is None:
#                 continue
#             TGUser.create(
#                 student=student,
#                 tg_id=user.tg_id,
#                 username=user.tg_username,
#                 fullname=user.tg_fullname
#             )


if __name__ == '__main__':
    pass
    # migrate_tg_data()
