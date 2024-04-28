select student.id_, count(*) с, student.name
from ban join student on ban.student_id = student.id_
group by student.name
order by с desc;