select event, task_id, group_concat(distinct name), count(distinct student_id) c
from run
         join main.submission s on s.id_ = run.submission_id
         join main.student s2 on s2.id_ = s.student_id
where verdict = 'OK'
group by event, task_id, solution_hash
having c > 1;

select st1.name, rsst2.name, count(distinct r1.solution_hash) c
from run r1
         join submission s1 on r1.submission_id = s1.id_
         join student st1 on s1.student_id = st1.id_
         join (select *
               from run r2
                        join submission s2 on r2.submission_id = s2.id_
                        join student st2 on s2.student_id = st2.id_) rsst2
              on r1.solution_hash = rsst2.solution_hash
                  and r1.task_id = rsst2.task_id
                  and s1.student_id < rsst2.student_id
-- where r1.verdict = 'OK' and rsst2.verdict = 'OK'
group by s1.student_id, rsst2.student_id
having c > 0
order by c desc;