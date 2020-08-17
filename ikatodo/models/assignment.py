from typing import Dict
from datetime import date
from dataclasses import dataclass


@dataclass
class Dates(object):
    doable_date: date
    due_date: date


@dataclass
class BasicInfo(object):
    course_id: str
    name: str
    dates: Dates
    id: str
    ref_url: str

@dataclass
class Assignment(object):
    basic_info: BasicInfo
    segment_number: int
    scheduled: bool
    office_hour: bool
    status: str

    def to_update_record(self):
        return{
            "fields": {
                "Assignment Name": self.basic_info.course_id + " " + self.basic_info.name,
                "Number of Segments": self.segment_number,
                "Doable Date":  self.basic_info.dates.doable_date.strftime("%Y-%m-%d"),
                "Due Date":  self.basic_info.dates.due_date.strftime("%Y-%m-%d"),
                "Type": "Assignment",
                "Scheduled?": "true" if self.scheduled else "false",
                "Status": self.status,
                "Office Hour?": self.office_hour
            }}
