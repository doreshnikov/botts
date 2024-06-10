select ok.task_id, ok.cnt, wrong.cnt, 1.0 * ok.cnt / (ok.cnt + wrong.cnt) as ratio
from (select task_id, count(distinct student_id) as cnt
      from run
               join submission on run.submission_id = submission.id_
               join student on submission.student_id = student.id_
      where run.verdict = 'OK'
        and event = 'homework-03'
      group by run.task_id) as ok
         join
     (select stats_all.task_id, count(distinct stats_all.student_id) as cnt
      from (select task_id, student_id, count(*) as cnt
            from run
                     join submission on run.submission_id = submission.id_
                     join student on submission.student_id = student.id_
            group by task_id, student_id) as stats_all
               join
           (select task_id, student_id, count(*) as cnt
            from run
                     join submission on run.submission_id = submission.id_
                     join student on submission.student_id = student.id_
            where verdict != 'OK'
            group by task_id, student_id) as stats_wrong
           on stats_all.task_id = stats_wrong.task_id and stats_all.student_id = stats_wrong.student_id
      where stats_all.cnt = stats_wrong.cnt
      group by stats_all.task_id) as wrong
     on ok.task_id = wrong.task_id;