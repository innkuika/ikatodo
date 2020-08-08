import datetime
import requests
from global_var import GlobalVar
from airtableapiclient import AirtableApiClient
from typing import Dict, List
from work_models import Assignment
from todo_models import Todo
from officehour_models import OfficeHour
from metacache import Metacache
from time import strftime, gmtime

gv = GlobalVar()


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


def generate_assignment_todos(assignment: Assignment) -> List[Todo]:
    todos = []
    work_peroid_and_load = calc_assignment_workload_distribution(assignment)
    for date in work_peroid_and_load:
        load = work_peroid_and_load[date]
        if load == 0:
            continue
        assignment_name = assignment.basic_info.course_id + ' ' + \
                          assignment.basic_info.name + '(' + str(load) + ')'
        description = ''
        todo = Todo(
            assignment_name, date, assignment.basic_info.ref_url, assignment.basic_info.id, description, "Assignment", '')
        todos.append(todo)
    return todos


def generate_ddl_reminder(assignment: Assignment) -> Todo:
    assignment_info = assignment.basic_info
    assignment_name = assignment_info.course_id + ' ' + assignment.basic_info.name
    description = ''
    reminder = Todo(assignment_name, assignment_info.dates.due_date,
                    assignment_info.ref_url, assignment_info.id, description, "DDL Reminder", '')
    return reminder


def update_related_assignment(assignment: Assignment):
    assignment_id = assignment.basic_info.id
    record = assignment.to_update_record()
    response = requests.patch(
        f'{gv.WORK_URL}/{assignment_id}', json=record, headers=gv.HEADERS)

    if response.status_code != 200:
        raise Exception('Failed to update related assignment.\n {}'.format(response.json()))


def post_new_assignment_todos(metacache: Metacache):
    assignments = metacache.metastore.get_not_scheduled_assignments()
    for assignment in assignments:
        todos = generate_assignment_todos(assignment)
        for todo in todos:
            todo_record = todo.to_post_record()
            response = requests.post(
                gv.TODO_URL, json=todo_record, headers=gv.HEADERS)

            if response.status_code != 200:
                raise Exception('Failed to post assignment todo. {}'.format(response.json()))

        # generate and post DDL reminder for each assignment
        reminder_record = generate_ddl_reminder(assignment).to_post_record()
        response = requests.post(
            gv.TODO_URL, json=reminder_record, headers=gv.HEADERS)
        if response.status_code != 200:
            raise Exception('Failed to post DDL reminder. {}'.format(response.json()))

        assignment.scheduled = True
        update_related_assignment(assignment)


def generate_office_hour_reminder_description(office_hour: OfficeHour, assignment: Assignment) -> str:
    host = office_hour.host
    location = office_hour.location
    time_begin = strftime("%H:%M", gmtime(office_hour.time_begin))
    time_end = strftime("%H:%M", gmtime(office_hour.time_end))
    current_assignment_name = assignment.basic_info.name

    description = f"Meet {host} at {location} form {time_begin} to {time_end}. \n" \
                  f"Current assignment: {current_assignment_name}"
    return description


def generate_office_hour_reminder(metacache: Metacache, assignment: Assignment) -> Todo:
    assignment_info = assignment.basic_info
    assignment_name = assignment_info.course_id + ' ' + assignment.basic_info.name
    office_hour, date = metacache.get_next_office_hour(assignment_info.course_id)
    description = generate_office_hour_reminder_description(office_hour, assignment)

    office_hour_reminder = Todo(assignment_name, date, assignment_info.ref_url, assignment_info.id,
                                description, "Office Hour Reminder")
    return office_hour_reminder


def post_new_office_hour_reminders(metacache: Metacache):
    assignments = metacache.metastore.get_all_assignments()
    for assignment in assignments:
        if assignment.office_hour:
            reminder_record = generate_office_hour_reminder(metacache, assignment).to_post_record()

            response = requests.post(
                gv.TODO_URL, json=reminder_record, headers=gv.HEADERS)

            if response.status_code != 200:
                raise Exception('Failed to post office hour reminder. {}'.format(response.json()))

            assignment.office_hour = False
            assignment.status = "Waiting for Help"
            update_related_assignment(assignment)


def update_todo(todo: Todo) -> int:
    todo_id = todo.id
    record = todo.to_post_record()
    response = requests.patch(
        f'{gv.TODO_URL}/{todo_id}', json=record, headers=gv.HEADERS)

    return response.status_code


def reassign_overdue_assignment_todos(metacache: Metacache):
    overdue_assignment_todos = metacache.get_overdue_assignment_todos()
    for todo in overdue_assignment_todos:
        response = update_todo(todo)
        if response != 200:
            raise Exception('Failed to update overdue assignment todos.\n {}'.format(response.json()))


def main():
    metacache = Metacache(AirtableApiClient(gv))

    post_new_assignment_todos(metacache)
    post_new_office_hour_reminders(metacache)

    reassign_overdue_assignment_todos(metacache)

    # metacache.metastore.delete_all_todos()

    # json_formatted_str = json.dumps(record, indent=2)
    # print(json_formatted_str)


if __name__ == '__main__':
    main()
