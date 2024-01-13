select * from run
join main.submission s on s.id_ = run.submission_id
join main.student s2 on s2.id_ = s.student_id
where name = 'Вертакова Дарья Николаевна' and verdict = 'OK' and event = 'contest-02';