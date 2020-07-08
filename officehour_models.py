from typing import Dict

class OfficeHour(object):
    def __init__(self, course_id: str, host: str, role: str, location: str, day: int, time_begin: int, duration: int):
        self.course_id = course_id
        self.host = host
        self.role = role
        self.location = location
        self.day = day
        self.time_begin = time_begin
        self.duration = duration

    def to_json(self):
        return{
            "Coures ID": self.course_id,
            "Host": self.host,
            "Location": self.location,
            "Day": self.day,
            "Time Begin": str(self.time_begin),
            "Role": self.role,
            "Duration": str(self.duration)
        }