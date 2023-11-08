from botts.db.student import Student
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


if __name__ == '__main__':
    print(list(Master.runs(20, 0, DBFilter('submission', 'id', '<', 5))))
    print(list(Master.runs(20, 0)))
    print(Master.runs_count(DBFilter('student', 'id', '<', 70)))
