from dataclasses import dataclass


@dataclass
class OfficeHour(object):
    course_id: str
    host: str
    role: str
    location: str
    day: int
    time_begin: int
    time_end: int

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