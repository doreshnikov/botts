select student.id_, count(*), student.name
from ban join student on ban.student_id = student.id_
group by student.name;