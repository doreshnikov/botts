from botts.testsys.components.base.event import Submission

from ..artefacts import Artefactory
from ..pipeline import Step
from ..testing import SUBMISSION, JURY_SOLUTION, CODE


class Wrapping(Step):
    def __init__(self):
        super().__init__([SUBMISSION], [JURY_SOLUTION, CODE])
    
    @Step.resolve_artefacts(submission=SUBMISSION)
    def process(self, a: Artefactory, submission: Submission):
        if submission.task.executor is None:
            return
        a[JURY_SOLUTION] = submission.task.executor.wrap_callable(submission.task.solution)
        a[CODE] = submission.task.executor.wrap_source(submission.solution)


