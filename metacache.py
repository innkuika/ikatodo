from metastore import Metastore
from work_models import Assignment
from officehour_models import OfficeHour
from typing import Tuple
import datetime


class Metacache(object):
    def __init__(self, metastore: Metastore):
        self.metastore = metastore

    def get_assignment_id(self) -> str:
        pass
    
    def get_assignment_by_id(self) -> Assignment:
        pass

    def get_next_office_hour(self, course_id: str) -> Tuple[OfficeHour, datetime.date]:
        # starting tomorrow
        date = (datetime.datetime.now()+datetime.timedelta(days=1)).date()
        office_hours = sorted(self.metastore.get_office_hour_by_course_id(course_id), key=lambda x: x.day, reverse=True)
        while True:
            for office_hour in office_hours:
                if date.weekday() == office_hour.day:
                    return office_hour, date
            date += datetime.timedelta(days=1)



