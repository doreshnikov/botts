from random import Random
from typing import Callable

from .artefacts import Artefact, ArtefactCollection, Artefactory
from .pipeline import Step, Pipeline, InterruptPipeline

from botts.testsys.components.base.event import Submission
from botts.testsys.components.process.generate import Arguments
from botts.testsys.components.run.invoker_pool import InvokerPool, FailedContainerException
from botts.testsys.components.run.runner import safe_run

from common.testsys.runner import Verdict, JudgeFeedback, TestingResult, JudgeSignature, TestingRequest, TestingResponse

# Artefacts

SUBMISSION = Artefact('@testing/submission', Submission)
JURY_SOLUTION = Artefact('@testing/jury_solution', Callable)
CODE = Artefact('@testing/code', str)

TESTS = ArtefactCollection('@testing/tests', Arguments, group='test')
EXPECTED_VALUES = ArtefactCollection('@testing/expected_values', object, group='test')
JUDGE_REQUESTS = ArtefactCollection('@testing/judge_resuests', TestingRequest, group='test')
TESTING_RESULTS = ArtefactCollection('@testing/testing_results', TestingResult, group='test')

RESULT = Artefact('@testing/result', JudgeFeedback)
ERRORS = ArtefactCollection('@testing/errors', Exception, group='errors')

# Steps

class Validation(Step):
    def __init__(self):
        super().__init__([SUBMISSION], [RESULT])
    
    @Step.resolve_artefacts(submission=SUBMISSION)
    def process(self, a: Artefactory, submission: Submission):
        result = JudgeFeedback(Verdict.CF, None)
        a[RESULT] = result
        
        message = submission.task.validator.validate(submission.solution)
        if message is None:
            result.verdict = Verdict.VE
            result.message = message
            raise InterruptPipeline()
        
        result.verdict = Verdict.OK
        

class Generation(Step):
    def __init__(self, seed: int):
        super().__init__([SUBMISSION], [TESTS, JURY_SOLUTION, CODE, ERRORS])
        self.seed = seed
        
    @Step.resolve_artefacts(submission=SUBMISSION)
    def process(self, a: Artefactory, submission: Submission):
        rnd = Random(self.seed)
        a[TESTS] = submission.task.generate_tests(rnd)
        a[JURY_SOLUTION] = submission.task.solution
        a[CODE] = submission.solution.source
        a[ERRORS] = []
        

class Preparing(Step):
    def __init__(self, seed: int):
        super().__init__([SUBMISSION, TESTS.item, CODE], [JUDGE_REQUESTS.item])
        self.seed = seed
    
    @Step.resolve_artefacts(submission=SUBMISSION, code=CODE)
    def process(self, a: Artefactory, submission: Submission, test: tuple[int, Arguments], code: str):
        _, test = test
        a[JUDGE_REQUESTS.item] = TestingRequest(code, test.args, test.kwargs, submission.task.time_limit)


class RunningModel(Step):
    def __init__(self):
        super().__init__([JURY_SOLUTION, TESTS.item, ERRORS], [EXPECTED_VALUES.item, TESTING_RESULTS.item])
        
    @Step.resolve_artefacts(solution=JURY_SOLUTION, test=TESTS.item, errors=ERRORS)
    def process(self, a, solution: Callable, test: tuple[int, Arguments], errors: list[Exception]):
        index, test = test
        result = TestingResult(JudgeFeedback(Verdict.OK, None), None, None)
        a[TESTING_RESULTS.item] = result
        
        try:
            value = safe_run(solution, test.args, test.kwargs)
        except Exception as e:
            result.feedback = JudgeFeedback(Verdict.CF, f'[test {index + 1}] error while running correct solution: {e}')
            errors.append(e)
            raise InterruptPipeline()
        
        a[EXPECTED_VALUES.item] = value


class Judging(Step):
    def __init__(self, pool: InvokerPool):
        super().__init__([JUDGE_REQUESTS.item, TESTING_RESULTS.item, ERRORS], [])
        self.pool = pool
        
    @Step.resolve_artefacts(request=JUDGE_REQUESTS.item, testing_result=TESTING_RESULTS.item, errors=ERRORS)
    def process(self, _, request: tuple[int, TestingRequest], testing_result: tuple[int, TestingResult], errors: list[Exception]):
        index, request = request
        _, testing_result = testing_result
        if testing_result.verdict != Verdict.OK:
            # TODO add logging
            return
        
        invoker = self.pool.acquire()
        invoker_id, invoker_port = invoker.id_, invoker.port
        testing_result.signature = JudgeSignature(invoker_id, invoker_port)
        
        with invoker:
            try:
                invoker.send(request)
                run_response: TestingResponse = invoker.receive()
            except FailedContainerException as e:
                testing_result.feedback = JudgeFeedback(Verdict.CF, f'[test {index + 1}] invoker {invoker_id}:{invoker_port} failed')
                errors.append(e)
                raise InterruptPipeline()
        
        testing_result.feedback = JudgeFeedback(run_response.verdict, run_response.message)
        testing_result.value = run_response.value


class Checking(Step):
    def __init__(self):
        super().__init__([SUBMISSION, TESTS.item, EXPECTED_VALUES.item, TESTING_RESULTS.item, RESULT], [])
        
    @Step.resolve_artefacts(submission=SUBMISSION, test=TESTS.item, expected_value=EXPECTED_VALUES.item, testing_result=TESTING_RESULTS.item, result=RESULT)
    def process(
        self, _, submission: Submission, 
        test: tuple[int, Arguments], expected_value: tuple[int, object], testing_result: tuple[int, TestingResult], result: JudgeFeedback
    ):
        index, test = test
        _, expected_value = expected_value
        _, testing_result = testing_result
        if testing_result.verdict != Verdict.OK:
            # TODO add logging
            return
        
        extended_info = {}
        if submission.task.extended_info:
            extended_info['student_id'] = submission.author.id_
        
        check_result = submission.task.checker.check(test, testing_result.value, expected_value, **extended_info)
        testing_result.feedback = check_result
        if check_result.verdict != Verdict.OK:
            testing_result.feedback.message = f'[test {index + 1}] {check_result.message}'
        return check_result
    

class Grading(Step):
    pass # TODO