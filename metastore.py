import requests
import json
from typing import List
from work_models import Assignment, Dates, BasicInfo
from todo_models import TodoAssignment
import datetime
import global_var as gv


class Metastore(object):
    def __init__(self):
        self.work_records = requests.get(gv.WORK_URL, headers=gv.HEADERS).json()['records']
        self.todo_records = requests.get(gv.TODO_URL, headers=gv.HEADERS).json()['records']

    def get_all_assignments(self) -> List[Assignment]:
        assignments = []
        for record in self.work_records:
            if record['fields']['Type'] == 'Assignment':
                dates = Dates(datetime.datetime.strptime(record['fields']['Available Date'], '%Y-%m-%d'),
                              datetime.datetime.strptime(record['fields']['Doable Date'], '%Y-%m-%d'),
                              datetime.datetime.strptime(record['fields']['Due Date'], '%Y-%m-%d'),
                              datetime.datetime.strptime(record['fields']['Office Hour Date'], '%Y-%m-%d'))
                basic_info = BasicInfo(record['fields']['Assignment Name'][:7],
                                       record['fields']['Assignment Name'][8:], dates, record['id'],
                                       record['fields']['Ref URL'] if ('Ref URL' in record['fields']) else ''
                                       )
                assignment = Assignment(
                    basic_info, 
                    record['fields']['Number of Segments'],
                    True if record['fields']['Scheduled?']== 'true' else False)
                assignments.append(assignment)
        return assignments
    
    # def get_all_todos(self) -> List[TodoAssignment]:
    #     todos = []
    #     for record in self.todo_records:
    #         todo = TodoAssignment(record['fields']['Name'],
    #        datetime.datetime.strptime(record['fields']['Date'], '%Y-%m-%d'),
    #         record['fields']['Ref URL'] if ('Ref URL' in record['fields']) else '',
    #         record['fields']['id'],


            # )

    def get_not_scheduled_assignments(self) -> List[Assignment]:
        assignments = []
        for assignment in self.get_all_assignments():
            if not assignment.scheduled:
                assignments.append(assignment)
        return assignments

    def delete_all_todos(self):
        for record in self.todo_records:
            id = record["id"]
            response = requests.delete(f"{gv.TODO_URL}/{id}",  headers=gv.HEADERS)
            if(response.status_code != 200):
                print(response.json())

