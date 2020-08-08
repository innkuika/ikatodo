import datetime
from .airtable_api_client import AirtableApiClient
from .models import OfficeHour, Todo
from typing import Tuple, List


class ApiWrapper(object):
    def __init__(self, api_client: AirtableApiClient):
        self.api_client = api_client

    def get_next_office_hour(self, course_id: str) -> Tuple[OfficeHour, datetime.date]:
        # starting tomorrow
        tomorrow_date = (datetime.datetime.now()+datetime.timedelta(days=1)).date()
        office_hours = sorted(self.api_client.get_office_hour_by_course_id(course_id), key=lambda x: x.day, reverse=True)
        for day_count in range(180):
            for office_hour in office_hours:
                if tomorrow_date.weekday() == office_hour.day:
                    return office_hour, tomorrow_date
            tomorrow_date += datetime.timedelta(days=1)
        raise Exception('Did not find possible date to schedule office hour within 180 days.')

    def get_overdue_assignment_todos(self) -> List[Todo]:
        todos = self.api_client.get_all_todos()
        overdue_assignment_todos = []
        date = datetime.datetime.now()
        for todo in todos:
            if todo.type == "Assignment" and todo.date < date:
                # update todos' date to today
                todo.date = date
                overdue_assignment_todos.append(todo)

        return overdue_assignment_todos

