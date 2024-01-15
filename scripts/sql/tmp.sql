select * from compression_rate
join main.student s on s.id_ = compression_rate.student_id
order by rate desc;