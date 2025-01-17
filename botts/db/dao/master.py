import textwrap

from botts.db.student import Student

from .. import database

from ..run import Run
from ..submission import Submission
from ..util.filter import DBFilter


class Master:
    """
    TODO optimize this shit
    """
    _MODELS = [Run, Submission, Student]

    @staticmethod
    def _base():
        return (Run
                .select(Run, Submission, Student)
                .join(Submission)
                .join(Student))

    @staticmethod
    def runs_count(*filters: DBFilter):
        query = (Master
                 ._base()
                 .where(DBFilter.join_filters(filters)))
        return query.count()

    @staticmethod
    def runs(limit: int | None, offset: int | None, *filters: DBFilter):
        query = (Master
                 ._base()
                 .where(DBFilter.join_filters(filters))
                 .order_by(Submission.timestamp)
                 .limit(limit)
                 .offset(offset))
        return query.execute()


class Cheating:
    @staticmethod
    def student_matches(student_id: int) -> dict[tuple[int, str], list[int, str]]:
        cursor = database.execute_sql(textwrap.dedent('''
            select s.id_, s.name, run.task_id, run.id_
            from run
                join submission sub on sub.id_ = run.submission_id
                join student s on s.id_ = sub.student_id
            where
                run.verdict = 'OK' and
                s.id_ != ? and
                (run.task_id, run.solution_hash) in (
                    select run.task_id, run.solution_hash
                    from run
                        join submission sub on sub.id_ = run.submission_id
                        join student s on s.id_ = sub.student_id
                    where s.id_ = ? and
                    run.verdict = 'OK'
                )
        '''), (student_id, student_id))
        
        matches = {}
        for row in cursor.fetchall():
            s_id, s_name, task_id, run_id = row
            key = (s_id, s_name)
            if key not in matches:
                matches[key] = []
            matches[key].append((run_id, task_id))
            
        return matches
    
    @staticmethod
    def get_run_by_hash(student_id: int, task_id: str, solution_hash: str) -> Run:
        query = (Run.select()
                 .join(Submission)
                 .join(Student)
                 .where((Student.id_ == student_id) & 
                        (Run.task_id == task_id) & 
                        (Run.solution_hash == solution_hash)))
        return query.first()
    
    @staticmethod
    def task_groups(task_id: int):
        cursor = database.execute_sql(textwrap.dedent('''
            select run.task_id, group_concat(distinct s.id_), group_concat(run.id_), count(distinct s.id_) c
            from run
                join submission sub on sub.id_ = run.submission_id
                join student s on s.id_ = sub.student_id
            where verdict = 'OK' and
                task_id = ?
            group by sub.event, run.task_id, run.solution_hash
            having c > 1;
        '''), (task_id,))
        
        return list(cursor.fetchall())


if __name__ == '__main__':
    print(list(Master.runs(20, 0, DBFilter('submission', 'id', '<', 5))))
    print(list(Master.runs(20, 0)))
    print(Master.runs_count(DBFilter('student', 'id', '<', 70)))
