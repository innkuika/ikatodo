from metastore import Metastore
from typing import Dict, List
from work_models import Assignment
from todo_models import TodoAssignment
import datetime
import json
import requests
import global_var as gv


def calc_assignment_workload_distribution(assignment: Assignment) -> Dict:
    worktime = (assignment.basic_info.dates.due_date -
                assignment.basic_info.dates.doable_date).days

    # distributes workload evenly
    num = assignment.segment_number
    div = worktime
    workload = [num // div + (1 if x < num % div else 0) for x in range(div)]

    distribution = {}
    date = assignment.basic_info.dates.doable_date
    for work in workload:
        distribution[date] = work
        date += datetime.timedelta(days=1)
    return distribution


def generate_assignment_todos(assignment: Assignment) -> List[TodoAssignment]:
    todos = []
    work_peroid_and_load = calc_assignment_workload_distribution(assignment)
    for date in work_peroid_and_load:
        load = work_peroid_and_load[date]
        if load == 0:
            continue
        assignment_name = assignment.basic_info.course_id + ' ' + \
            assignment.basic_info.name + '(' + str(load) + ')'
        todo = TodoAssignment(
            assignment_name, date, assignment.basic_info.ref_url, assignment.basic_info.id)
        todos.append(todo)
    return todos


def update_related_assignment(assignment: Assignment):
    # updates Scheduled? to true
    assignment.scheduled = True
    assignment_id = assignment.basic_info.id
    record = assignment.to_update_record()
    response = requests.patch(
        f'{gv.WORK_URL}/{assignment_id}', json=record, headers=gv.HEADERS)
    if(response.status_code != 200):
        print(response.status_code)
        print(response.json())
        return None


def post_new_assignment_todos():
    assignments = Metastore().get_not_scheduled_assignments()

    for assignment in assignments:
        todos = generate_assignment_todos(assignment)
        for todo in todos:
            todo_record = todo.to_post_record()
            response = requests.post(
                gv.TODO_URL, json=todo_record, headers=gv.HEADERS)

            # TODO: Throw error
            if(response.status_code != 200):
                print(response.json())
                return None
        update_related_assignment(assignment)


def main():
    gv.init()
    post_new_assignment_todos()

    # Metastore().delete_all_todos()


    # json_formatted_str = json.dumps(records, indent=2)
    # print(json_formatted_str)
main()
