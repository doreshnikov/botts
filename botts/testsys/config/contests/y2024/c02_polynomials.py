from datetime import datetime
import textwrap

from botts.testsys.components.base.task import Statement
from botts.testsys.components.test.event import Event

from botts.testsys.config.tasks.educ.math.polynomial.evaluate import TASK as _evaluate
from botts.testsys.config.tasks.educ.math.polynomial.add import TASK as _add
from botts.testsys.config.tasks.educ.math.polynomial.derivative import TASK as _derivative
from botts.testsys.config.tasks.educ.math.polynomial.multiply import TASK as _multiply
from botts.testsys.config.tasks.educ.math.polynomial.find_root import TASK as _find_root
from botts.testsys.config.tasks.educ.math.polynomial.to_string import TASK as _to_string
from botts.testsys.config.tasks.educ.math.polynomial.divide import TASK as _divide

EVENT = Event(
    '02-polynomials',
    datetime(year=2024, month=10, day=22, hour=0, minute=0, second=0),
    datetime(year=2025, month=1, day=16, hour=21, minute=0, second=0),
    [_evaluate, _add, _derivative, _multiply, _find_root, _to_string, _divide],
    statement_prefix=Statement(
        md=textwrap.dedent('''
        `POLYNOMIALS`
        
        В этом контесте вам предстоит работа с многочленами. Каждый из них задается массивом 
        своих коэффициентов: `[0, 2, 1]` соответствует `2x + x^2`. Иными словами, `i`-й 
        элемент массива задает коэффициент при `i`-й степени неизвестной.
        Для вашего удобства во всех задачах будет доступен тип `polynomial = list[int | float]`.
        
        По умолчанию ожидается, что все возвращаемые вашими решениями многочлены находятся в 
        нормальной форме (не имеют лишних ведущих нулей). Если вы не соблюдаете нормальную 
        форму, вы можете получить вердикт `WA`.
        ''')
    )
)
