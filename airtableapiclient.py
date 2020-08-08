import requests
from global_var import GlobalVar
from typing import List
from work_models import Assignment, Dates, BasicInfo
from todo_models import Todo
from officehour_models import OfficeHour
import datetime


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
        self.work_records = requests.get(
            gv.WORK_URL, headers=gv.HEADERS).json()['records']
        self.todo_records = requests.get(
            gv.TODO_URL, headers=gv.HEADERS).json()['records']
        self.office_hour_records = requests.get(
            gv.OH_URL, headers=gv.HEADERS).json()['records']

    def get_all_assignments(self) -> List[Assignment]:
        assignments = []
        for record in self.work_records:
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

    def get_assignments_need_oh(self) -> List[Assignment]:
        assignments = []
        for assignment in self.get_all_assignments():
            if assignment.office_hour:
                assignments.append(assignment)
        return assignments

    def get_all_todos(self) -> List[Todo]:
        todos = []
        for record in self.todo_records:
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

    def get_all_office_hours(self) -> List[OfficeHour]:
        office_hours = []
        for record in self.office_hour_records:
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

    def get_office_hour_by_course_id(self, course_id: str) -> List[OfficeHour]:
        office_hours = []
        for office_hour in self.get_all_office_hours():
            if course_id == office_hour.course_id:
                office_hours.append(office_hour)
        return office_hours

    def get_not_scheduled_assignments(self) -> List[Assignment]:
        assignments = []
        for assignment in self.get_all_assignments():
            if not assignment.scheduled:
                assignments.append(assignment)
        return assignments

    def delete_all_todos(self):
        for record in self.todo_records:
            id = record["id"]
            response = requests.delete(
                f"{self.gv.TODO_URL}/{id}",  headers=self.gv.HEADERS)
            if(response.status_code != 200):
                print(response.json())
