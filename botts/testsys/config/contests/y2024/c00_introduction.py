from datetime import datetime

from botts.testsys.components.test.event import Event

from botts.testsys.config.tasks.test.whoami import TASK as _whoami
from botts.testsys.config.tasks.test.unique import TASK as _unique

EVENT = Event(
    '00-introduction',
    datetime(year=2024, month=10, day=7, hour=21, minute=0, second=0),
    datetime(year=2024, month=10, day=14, hour=0, minute=0, second=0),
    [_whoami, _unique]
)
