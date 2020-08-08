import requests
import datetime
from typing import List
from requests import Response
from .global_var import GlobalVar
from .models import OfficeHour, BasicInfo, Todo, Assignment, Dates


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
    def __init__(self, gv: GlobalVar):
        self.gv = gv

    @staticmethod
    def _handle_bad_response(response: Response):
        if response.status_code != 200:
            raise Exception(f'Failed to post to {response.request.url}. '
                            f'Request body {response.request.body}. '
                            f'Response {response.json()}. '
                            f'Status code {response.status_code}.')

    def get_all_assignments(self) -> List[Assignment]:
        assignments = []
        assignment_records = requests.get(
            self.gv.ASSIGNMENTS_URL, headers=self.gv.HEADERS
        ).json()['records']
        for record in assignment_records:
            if record['fields']['Type'] == 'Assignment':
                dates = Dates(datetime.datetime.strptime(record['fields']['Available Date'], '%Y-%m-%d'),
                              datetime.datetime.strptime(
                                  record['fields']['Doable Date'], '%Y-%m-%d'),
                              datetime.datetime.strptime(
                                  record['fields']['Due Date'], '%Y-%m-%d'),
                              datetime.datetime.strptime(record['fields']['Office Hour Date'], '%Y-%m-%d'))
                basic_info = BasicInfo(record['fields']['Assignment Name'][:7],
                                       record['fields']['Assignment Name'][8:], dates, record['id'],
                                       record['fields']['Ref URL'] if (
                                           'Ref URL' in record['fields']) else ''
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
        self._handle_bad_response(
            requests.patch(f'{self.gv.ASSIGNMENTS_URL}/{assignment_id}', json=record, headers=self.gv.HEADERS)
        )

    def get_all_todos(self) -> List[Todo]:
        todos = []
        todo_records = requests.get(
            self.gv.TODO_URL, headers=self.gv.HEADERS
        ).json()['records']
        for record in todo_records:
            todo = Todo(record['fields']['Name'],
                        datetime.datetime.strptime(
                                      record['fields']['Date'], '%Y-%m-%d'),
                        record['fields']['Ref URL'] if (
                                      'Ref URL' in record['fields']) else '',
                        record['fields']['Related Work ID'],
                        record['fields']['Description'] if 'Description' in record['fields'] else '',
                        record['fields']['Type'],
                        record['id'])
            todos.append(todo)
        return todos

    def post_todo(self, todo: Todo):
        todo_record = todo.to_post_record()
        self._handle_bad_response(requests.post(
            self.gv.TODO_URL,
            json=todo_record,
            headers=self.gv.HEADERS
        ))

    def get_all_office_hours(self) -> List[OfficeHour]:
        office_hours = []
        office_hour_records = requests.get(
            self.gv.OH_URL, headers=self.gv.HEADERS
        ).json()['records']
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
