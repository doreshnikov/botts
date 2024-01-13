select name, task_id, count(*) > 0
from run
         join submission on submission.id_ = submission_id
         join student on submission.student_id = student.id_
where
    run.verdict = 'OK' and
    submission.event = 'contest-02'
group by name, task_id;