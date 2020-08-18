import datetime
from .airtable_api_client import AirtableApiClient
from .models import OfficeHour, Todo, Assignment
from typing import Tuple, List


class ApiWrapper(object):
    """
    Object to perform additional computations based on Airtable API call results
    """
    def __init__(self, api_client: AirtableApiClient):
        self.api_client = api_client

    def get_overdue_assignment_todos(self) -> List[Todo]:
        todos = self.api_client.get_all_todos()
        overdue_assignment_todos = []
        date = datetime.datetime.now().date()
        for todo in todos:
            if todo.type == "Assignment" and todo.date < date:
                # update todos' date to today
                todo.date = date
                overdue_assignment_todos.append(todo)

        return overdue_assignment_todos

    def get_assignments_need_oh(self) -> List[Assignment]:
        assignments = []
        for assignment in self.api_client.get_all_assignments():
            if assignment.office_hour:
                assignments.append(assignment)
        return assignments

    def get_unscheduled_assignments(self) -> List[Assignment]:
        assignments = []
        for assignment in self.api_client.get_all_assignments():
            if not assignment.scheduled:
                assignments.append(assignment)
        return assignments

    def get_office_hour_by_course_id(self, course_id: str) -> List[OfficeHour]:
        office_hours = []
        for office_hour in self.api_client.get_all_office_hours():
            if course_id == office_hour.course_id:
                office_hours.append(office_hour)
        return office_hours

    def get_next_office_hour(self, course_id: str) -> Tuple[OfficeHour, datetime.date]:
        # starting tomorrow
        tomorrow_date = (datetime.datetime.now()+datetime.timedelta(days=1)).date()
        office_hours = sorted(self.get_office_hour_by_course_id(course_id), key=lambda x: x.day, reverse=True)
        for day_count in range(180):
            for office_hour in office_hours:
                if tomorrow_date.weekday() == office_hour.day:
                    return office_hour, tomorrow_date
            tomorrow_date += datetime.timedelta(days=1)
        raise Exception('Did not find possible date to schedule office hour within 180 days.')

    def get_last_office_hour_date(self, assignment: Assignment) -> datetime.date:
        due_date = assignment.basic_info.dates.due_date
        course_id = assignment.basic_info.course_id

        # use today as the begin date if doable date is earlier than today
        begin_date = assignment.basic_info.dates.doable_date \
            if assignment.basic_info.dates.doable_date > datetime.datetime.now().date() \
            else datetime.datetime.now().date()
        end_date = assignment.basic_info.dates.due_date
        # total time to finish the assignment
        days = (end_date - begin_date).days

        office_hours = sorted(self.get_office_hour_by_course_id(course_id), key=lambda x: x.day, reverse=False)

        for day_count in range(days):
            for office_hour in office_hours:
                if due_date.weekday() == office_hour.day:
                    return due_date
            due_date -= datetime.timedelta(days=1)
        print(f'WARNING: Did not find office hour during assignment:'
              f'{assignment.basic_info.course_id} {assignment.basic_info.name}')
        return due_date
