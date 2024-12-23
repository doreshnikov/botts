from datetime import datetime
import textwrap

from botts.testsys.components.base.task import Statement
from botts.testsys.components.test.event import Event

from botts.testsys.config.tasks.educ.recursion.function import TASK as _function
from botts.testsys.config.tasks.misc.new_year_tree import TASK as _new_year_tree
from botts.testsys.config.tasks.misc.oeis.new_year import TASK as _new_year_sequence
from botts.testsys.config.tasks.educ.files.compress import TASK as _compress # TODO fix and add

EVENT = Event( 
    '03-variety',
    datetime(year=2024, month=12, day=23, hour=0, minute=0, second=0),
    datetime(year=2025, month=1, day=16, hour=21, minute=0, second=0),
    [_function, _new_year_tree, _new_year_sequence],
    statement_prefix=Statement(
        md=textwrap.dedent('''
        `VARIETY`
        
        В этом контесте вам предстоит решить по одной небольшой задаче на менее базовые темы. 
        Среди этих тем: рекурсия, работа с файлами, и новогодние бонусы.
        ''')
    )
)
