from typing import Dict
from datetime import date
from dataclasses import dataclass


@dataclass
class Dates(object):
    available_date: date
    doable_date: date
    due_date: date
    office_hour_date: date

    def to_json(self) -> Dict:
        return{
            "available_date": self.available_date,
            "doable_date": self.doable_date,
            "due_date": self.due_date,
            "office_hour_date": self.office_hour_date,
        }   


@dataclass
class BasicInfo(object):
    course_id: str
    name: str
    dates: Dates
    id: str
    ref_url: str

    def to_json(self) -> Dict:
        return{
            "course_id": self.course_id,
            "name": self.name,
            "dates": self.dates.to_json(),
            "ref_url": self.ref_url
        }


@dataclass
class Assignment(object):
    basic_info: BasicInfo
    segment_number: int
    scheduled: bool
    office_hour: bool
    status: str

    def to_json(self) -> Dict:
        return{
            "basic_info": self.basic_info.to_json(),
            "segment_number": self.segment_number,
            "scheduled": self.scheduled,
            "status": self.status,
            "office_hour": self.office_hour
        }

    def to_update_record(self):
        return{
            "fields": {
                "Assignment Name": self.basic_info.course_id + " " + self.basic_info.name,
                "Number of Segments": self.segment_number,
                "Available Date": self.basic_info.dates.available_date.strftime("%Y-%m-%d"),
                "Doable Date":  self.basic_info.dates.doable_date.strftime("%Y-%m-%d"),
                "Office Hour Date":  self.basic_info.dates.office_hour_date.strftime("%Y-%m-%d"),
                "Due Date":  self.basic_info.dates.due_date.strftime("%Y-%m-%d"),
                "Type": "Assignment",
                "Scheduled?": "true" if self.scheduled else "false",
                "Status": self.status,
                "Office Hour?": self.office_hour
            }}
