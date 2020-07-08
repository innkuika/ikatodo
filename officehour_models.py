from typing import Dict

class OfficeHour(object):
    def __init__(self, course_id: str, host: str, role: str, location: str, day: int, time_begin: int, time_end: int):
        self.course_id = course_id
        self.host = host
        self.role = role
        self.location = location
        self.day = day
        self.time_begin = time_begin
        self.time_end = time_end

    def to_json(self):
        return{
            "Coures ID": self.course_id,
            "Host": self.host,
            "Location": self.location,
            "Day": self.day,
            "Time Begin": str(self.time_begin),
            "Role": self.role,
            "Time End": str(self.time_end)
        }