from metastore import Metastore
from typing import Dict, List
from work_models import Assignment
import datetime
import json

def calc_assignment_workload_distribution(assignment: Assignment) -> Dict[str, int]:
    worktime = (assignment.basic_info.dates.due_date - assignment.basic_info.dates.doable_date).days

    # distributes workload evenly
    num = assignment.segment_number
    div = worktime
    workload = [num // div + (1 if x < num % div else 0)  for x in range (div)]

    distribution = {}
    date = assignment.basic_info.dates.doable_date
    for work in workload:
        distribution[date.strftime("%Y-%m-%d")] = work
        date += datetime.timedelta(days=1)
    return distribution

def generate_assignment_todo_rec(assignments: List[Assignment]) -> Dict[str, List]:
    records = {"records": []} 
    for assignment in assignments:
        work_peroid_and_load = calc_assignment_workload_distribution(assignment)
        for date in work_peroid_and_load:
            load = work_peroid_and_load[date]
            if load == 0:
                continue
            assignment_name = assignment.basic_info.course_id + ' ' + assignment.basic_info.name + '(' + str(load) + ')'
            record = {"fields":{
                "Name": assignment_name,
                "Date": date,
                "Ref URL": assignment.basic_info.ref_url
            }}
            records["records"].append(record)
    # json_formatted_str = json.dumps(records, indent=2)
    # print(json_formatted_str)
    return records


def main():
    assignments = Metastore().get_all_assignments()
    generate_assignment_todo_rec(assignments)


main()

