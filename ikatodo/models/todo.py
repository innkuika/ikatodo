from dataclasses import dataclass
from datetime import date


@dataclass
class Todo(object):
    name: str
    date: date
    ref_url: str
    related_work_id: str
    description: str
    type: str
    id: str
    status: str

    def to_post_record(self):
        reminder = ""
        if self.type == "DDL Reminder":
            reminder = "[DDL] "
        elif self.type == "Office Hour Reminder":
            reminder = "[OH] "

        return {
            "fields": {
                "Name": reminder + self.name,
                "Status": self.status,
                "Date": self.date.strftime("%Y-%m-%d"),
                "Description": self.description,
                "Ref URL": self.ref_url,
                "Related Work ID": self.related_work_id,
                "Type": self.type
            }
        }
