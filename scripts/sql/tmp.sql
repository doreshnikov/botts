select *
from run
         join main.submission s on s.id_ = run.submission_id
         join main.student s2 on s2.id_ = s.student_id
where run.verdict = 'OK'
  and s2.name like 'Черноблавская %'
  and s.event = 'homework-03';