import datetime
from typing import Dict, List
from time import strftime, gmtime
from .airtable_api_client import AirtableApiClient
from .models import Assignment, Todo, OfficeHour
from .api_wrapper import ApiWrapper


def calc_assignment_workload_distribution(assignment: Assignment, api_wrapper: ApiWrapper) -> Dict[datetime.date, int]:
    # use today as the begin date if doable date is earlier than today
    begin_date = assignment.basic_info.dates.doable_date \
        if assignment.basic_info.dates.doable_date > datetime.datetime.now().date() \
        else datetime.datetime.now().date()
    end_date = api_wrapper.get_last_office_hour_date(assignment)
    days = (end_date - begin_date).days

    # distributes workload evenly
    segments = assignment.segment_number
    workloads = [segments // days + (1 if x < segments % days else 0) for x in range(days)]

    distribution = {}
    for workload in workloads:
        distribution[begin_date] = workload
        begin_date += datetime.timedelta(days=1)
    return distribution


def generate_assignment_todos(assignment: Assignment, api_wrapper: ApiWrapper) -> List[Todo]:
    todos = []
    work_period_and_load = calc_assignment_workload_distribution(assignment, api_wrapper)
    for date, load in work_period_and_load.items():
        if load == 0:
            continue
        todo_name = f"{assignment.basic_info.course_id} {assignment.basic_info.name} ({str(load)})"
        todo = Todo(
            name=todo_name,
            date=date,
            ref_url=assignment.basic_info.ref_url,
            related_work_id=assignment.basic_info.id,
            description="",
            type="Assignment",
            id=''
        )
        todos.append(todo)
    return todos


def generate_ddl_reminder(assignment: Assignment) -> Todo:
    assignment_info = assignment.basic_info
    assignment_name = f"{assignment_info.course_id} {assignment.basic_info.name}"
    reminder = Todo(
        name=assignment_name,
        date=assignment_info.dates.due_date,
        ref_url=assignment_info.ref_url,
        related_work_id=assignment_info.id,
        description="",
        type="DDL Reminder",
        id=''
    )
    return reminder


def post_new_assignment_todos(api_wrapper: ApiWrapper):
    assignments = api_wrapper.get_unscheduled_assignments()
    for assignment in assignments:
        # generate and post todo for each assignment
        todos = generate_assignment_todos(assignment, api_wrapper)
        for todo in todos:
            api_wrapper.api_client.create_todo(todo)

        # generate and post DDL reminder for each assignment
        ddl_reminder = generate_ddl_reminder(assignment)
        api_wrapper.api_client.create_todo(ddl_reminder)

        # mark assignment as scheduled
        assignment.scheduled = True
        api_wrapper.api_client.update_assignment(assignment)


def generate_office_hour_reminder_description(office_hour: OfficeHour, assignment: Assignment) -> str:
    host = office_hour.host
    location = office_hour.location
    time_begin = strftime("%H:%M", gmtime(office_hour.time_begin))
    time_end = strftime("%H:%M", gmtime(office_hour.time_end))
    current_assignment_name = assignment.basic_info.name

    description = f"Meet {host} at {location} form {time_begin} to {time_end}. \n" \
                  f"Current assignment: {current_assignment_name}"
    return description


def generate_office_hour_reminder(api_wrapper: ApiWrapper, assignment: Assignment) -> Todo:
    assignment_info = assignment.basic_info
    assignment_name = assignment_info.course_id + ' ' + assignment.basic_info.name
    office_hour, date = api_wrapper.get_next_office_hour(assignment_info.course_id)
    description = generate_office_hour_reminder_description(office_hour, assignment)

    office_hour_reminder = Todo(assignment_name, date, assignment_info.ref_url, assignment_info.id,
                                description, "Office Hour Reminder", "")  # todo: ID?
    return office_hour_reminder


def post_new_office_hour_reminders(api_wrapper: ApiWrapper):
    assignments = api_wrapper.api_client.get_all_assignments()
    for assignment in assignments:
        if assignment.office_hour:
            # generate and post OH reminder
            reminder = generate_office_hour_reminder(api_wrapper, assignment)
            api_wrapper.api_client.create_todo(reminder)

            # mark assignment as waiting for help
            assignment.office_hour = False
            assignment.status = "Waiting for Help"
            api_wrapper.api_client.update_assignment(assignment)


def reassign_overdue_assignment_todos(api_wrapper: ApiWrapper):
    overdue_assignment_todos = api_wrapper.get_overdue_assignment_todos()
    for todo in overdue_assignment_todos:
        api_wrapper.api_client.update_todo(todo)


def run():
    print("Started!")
    api_wrapper = ApiWrapper(AirtableApiClient())
    api_wrapper.api_client.delete_all_todo()
    post_new_assignment_todos(api_wrapper)
    post_new_office_hour_reminders(api_wrapper)
    reassign_overdue_assignment_todos(api_wrapper)
    print("Finished, yayy!")
