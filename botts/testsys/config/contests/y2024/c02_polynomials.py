from datetime import datetime

from botts.testsys.components.test.event import Event

from botts.testsys.config.tasks.educ.math.polynomial.add import TASK as _add
from botts.testsys.config.tasks.educ.math.polynomial.derivative import TASK as _derivative
from botts.testsys.config.tasks.educ.math.polynomial.multiply import TASK as _multiply
from botts.testsys.config.tasks.educ.math.polynomial.find_root import TASK as _find_root
from botts.testsys.config.tasks.educ.math.polynomial.to_string import TASK as _to_string
from botts.testsys.config.tasks.educ.math.polynomial.to_latex import TASK as _to_latex
from botts.testsys.config.tasks.educ.math.polynomial.divide import TASK as _divide

EVENT = Event(
    '02-polynomials',
    datetime(year=2024, month=10, day=22, hour=0, minute=0, second=0),
    datetime(year=2024, month=11, day=17, hour=21, minute=0, second=0),
    [_add, _derivative, _multiply, _find_root, _to_string, _to_latex, _divide]
)
