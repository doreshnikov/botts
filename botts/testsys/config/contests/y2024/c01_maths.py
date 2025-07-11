from datetime import datetime

from botts.testsys.components.test.event import Event

from botts.testsys.config.tasks.educ.math.normal_cdf import TASK as _normal_cdf
from botts.testsys.config.tasks.educ.math.geom.angle import TASK as _angle
from botts.testsys.config.tasks.educ.math.geom.triangle_area import TASK as _triangle_area
from botts.testsys.config.tasks.educ.phys.highest_point import TASK as _highest_point
from botts.testsys.config.tasks.educ.phys.travel_distance import TASK as _travel_distance

EVENT = Event(
    '01-maths',
    datetime(year=2024, month=10, day=22, hour=0, minute=0, second=0),
    datetime(year=2024, month=12, day=26, hour=21, minute=0, second=0),
    [_normal_cdf, _angle, _triangle_area, _highest_point, _travel_distance]
)
