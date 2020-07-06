from typing import Dict
import datetime

class Dates(object):
    def __init__(self, available_date: datetime, doable_date: datetime, due_date: datetime, office_hour_date: datetime):
        self.available_date = available_date
        self.doable_date = doable_date
        self.due_date = due_date
        self.office_hour_date = office_hour_date,

    def to_json(self) -> Dict:
        return{
            "available_date": self.available_date,
            "doable_date": self.doable_date,
            "due_date": self.due_date,
            "office_hour_date": self.office_hour_date,
        }   

class BasicInfo(object):
    def __init__(self, course_id: str, name: str, dates: Dates, id: str, ref_url: str):
        self.course_id = course_id
        self.name = name
        self.dates = dates
        self.id = id
        self.ref_url = ref_url

    def to_json(self) -> Dict:
        return{
            "course_id": self.course_id,
            "name": self.name,
            "dates": self.dates.to_json(),
            "ref_url": self.ref_url
        }

class Assignment(object):
    def __init__(self, basic_info: BasicInfo, segment_number: int, scheduled: bool):
        self.basic_info = basic_info
        self.segment_number = segment_number
        self.scheduled = scheduled

    def to_json(self) -> Dict:
        return{
            "basic_info": self.basic_info.to_json(),
            "segment_number": self.segment_number,
            "scheduled": self.scheduled
        }
