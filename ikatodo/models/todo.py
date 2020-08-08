from typing import Dict
import datetime
from dataclasses import dataclass


@dataclass
class Todo(object):
    name: str
    date: datetime
    ref_url: str
    related_work_id: str
    description: str
    type: str
    id: str

    def to_json(self) -> Dict:
        return{
            "Name": self.name,
            "Date": self.date,
            "Ref URL": self.ref_url,
            "related assignment id": self.related_work_id,
            "Type": self.type,
            "Description": self.description
        }

    def to_post_record(self):
        reminder = ""
        if self.type == "DDL Reminder":
            reminder = "[DDL] "
        elif self.type == "Office Hour Reminder":
            reminder = "[OH] "

        return{"fields": {
                "Name": reminder + self.name,
                "Date": self.date.strftime("%Y-%m-%d"),
                "Description": self.description,
                "Ref URL": self.ref_url,
                "Related Work ID": self.related_work_id,
                "Type": self.type
            },
                "typecast": True}
