import requests
import json
from typing import List
from work_models import Assignment, Dates, BasicInfo
import datetime


class Metastore(object):
    def __init__(self):
        get_headers = {'Authorization': "Bearer keyx4zG23QYBXiRXN"}
        url = 'https://api.airtable.com/v0/app9aW8jJyqkeNcxP/Assignments'
        self.records = requests.get(url, headers=get_headers).json()['records']

    def get_all_assignments(self) -> List[Assignment]:
        assignments = []
        for record in self.records:
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
                    basic_info, record['fields']['Number of Segments'])
                assignments.append(assignment)
        return assignments
