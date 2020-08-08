from airtableapiclient import AirtableApiClient
from work_models import Assignment
from officehour_models import OfficeHour
from todo_models import Todo
from typing import Tuple, List
import datetime


class Metacache(object):
    def __init__(self, metastore: AirtableApiClient):
        self.metastore = metastore

    def get_assignment_id(self) -> str:
        pass
    
    def get_assignment_by_id(self) -> Assignment:
        pass

    def get_next_office_hour(self, course_id: str) -> Tuple[OfficeHour, datetime.date]:
        # starting tomorrow
        tomorrow_date = (datetime.datetime.now()+datetime.timedelta(days=1)).date()
        office_hours = sorted(self.metastore.get_office_hour_by_course_id(course_id), key=lambda x: x.day, reverse=True)
        for day_count in range(180):
            for office_hour in office_hours:
                if tomorrow_date.weekday() == office_hour.day:
                    return office_hour, tomorrow_date
            tomorrow_date += datetime.timedelta(days=1)
        raise Exception('Did not find possible date to schedule office hour within 180 days.')

    def get_overdue_assignment_todos(self) -> List[Todo]:
        todos = self.metastore.get_all_todos()
        overdue_assignment_todos = []
        date = datetime.datetime.now()
        for todo in todos:
            if todo.type == "Assignment" and todo.date < date:
                # update todos' date to today
                todo.date = date
                overdue_assignment_todos.append(todo)

        return overdue_assignment_todos

