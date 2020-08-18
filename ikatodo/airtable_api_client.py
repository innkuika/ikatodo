import os
import datetime
from typing import List
from requests import Response, Session
from .models import OfficeHour, BasicInfo, Todo, Assignment, Dates


def get_env_or_raise(key: str) -> str:
    if key not in os.environ:
        raise RuntimeError(f"{key} does not exist in environ")
    return os.environ[key]


WeekdayMapping = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}


class AirtableApiClient(object):
    """
    Object to directly make Airtable API calls without additional computations
    For additional computations please use ApiWrapper
    """
    def __init__(self):
        self.ASSIGNMENTS_URL = get_env_or_raise("ASSIGNMENTS_AIRTABLE_API")
        self.TODO_URL = get_env_or_raise("TODOS_AIRTABLE_API")
        self.OH_URL = get_env_or_raise("OFFICE_HOUR_AIRTABLE_API")
        self.COURSE_ID_LENGTH = get_env_or_raise("COURSE_ID_LENGTH")
        self.session = Session()
        self.session.headers.update({
            'Authorization': f"Bearer {get_env_or_raise('AUTH_TOKEN')}",
            'Content-Type': 'application/json'
        })

    @staticmethod
    def _raise_on_bad_response(response: Response):
        if response.status_code != 200:
            raise Exception(f'Failed to post to {response.request.url}. '
                            f'Request body {response.request.body}. '
                            f'Response {response.json()}. '
                            f'Status code {response.status_code}.')

    def get_all_assignments(self) -> List[Assignment]:
        assignments = []
        assignment_records = self.session.get(self.ASSIGNMENTS_URL).json()['records']
        course_id_length = self.COURSE_ID_LENGTH
        for record in assignment_records:
            if record['fields']['Type'] == 'Assignment':
                dates = Dates(due_date=datetime.datetime.strptime(
                                  record['fields']['Due Date'], '%Y-%m-%d').date(),
                              doable_date=datetime.datetime.strptime(
                                  record['fields']['Doable Date'], '%Y-%m-%d').date()
                              )
                basic_info = BasicInfo(course_id=record['fields']['Assignment Name'][:course_id_length],
                                       name=record['fields']['Assignment Name'][course_id_length+1:],
                                       dates=dates,
                                       id=record['id'],
                                       ref_url=record['fields']['Ref URL']
                                       if 'Ref URL' in record['fields'] else ''
                                       )
                assignment = Assignment(
                    basic_info,
                    record['fields']['Number of Segments'],
                    True if record['fields']['Scheduled?'] == 'true' else False,
                    True if 'Office Hour?' in record['fields'] else False,
                    record['fields']['Status'])
                assignments.append(assignment)
        return assignments

    def update_assignment(self, assignment: Assignment):
        assignment_id = assignment.basic_info.id
        record = assignment.to_update_record()
        self._raise_on_bad_response(
            self.session.patch(f'{self.ASSIGNMENTS_URL}/{assignment_id}', json=record)
        )

    def get_all_todos(self) -> List[Todo]:
        todos = []
        todo_records = self.session.get(self.TODO_URL).json()['records']
        for record in todo_records:
            todo = Todo(record['fields']['Name'],
                        datetime.datetime.strptime(
                                      record['fields']['Date'], '%Y-%m-%d').date(),
                        record['fields']['Ref URL'] if (
                                      'Ref URL' in record['fields']) else '',
                        record['fields']['Related Work ID'],
                        record['fields']['Description'] if 'Description' in record['fields'] else '',
                        record['fields']['Type'],
                        record['id'])
            todos.append(todo)
        return todos

    def create_todo(self, todo: Todo):
        todo_record = todo.to_post_record()
        self._raise_on_bad_response(self.session.post(self.TODO_URL, json=todo_record))

    def update_todo(self, todo: Todo):
        todo_id = todo.id
        record = todo.to_post_record()
        self._raise_on_bad_response(self.session.patch(f'{self.TODO_URL}/{todo_id}', json=record))

    def delete_todo(self, todo: Todo):
        todo_id = todo.id
        self._raise_on_bad_response(self.session.delete(f'{self.TODO_URL}/{todo_id}'))

    def get_all_office_hours(self) -> List[OfficeHour]:
        office_hours = []
        office_hour_records = self.session.get(self.OH_URL).json()['records']
        for record in office_hour_records:
            weekday = record['fields']["Day of Week"]
            office_hour = OfficeHour(record['fields']["Course ID"],
                                     record['fields']["Host"],
                                     record['fields']["Role"],
                                     record['fields']["Location"],
                                     WeekdayMapping[weekday],
                                     int(record['fields']["Time Begin"]),
                                     int(record['fields']["Time End"]))
            office_hours.append(office_hour)
        return office_hours

    def delete_all_todo(self):
        for todo in self.get_all_todos():
            self.delete_todo(todo)