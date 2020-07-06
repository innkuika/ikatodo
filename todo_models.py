from typing import Dict
import datetime

class DDLReminder(object):
    def __init__(self, name: str, date: datetime, ref_url: str, related_work_id: str):
        self.name = name
        self.date = date
        self.ref_url = ref_url
        self.related_work_id = related_work_id
        self.type = "DDL Reminder"
    
    def to_json(self) -> Dict:
        return{
            "Name": self.name,
            "Date": self.date,
            "Ref URL": self.ref_url,
            "related assignment id": self.related_work_id,
            "Type": self.type
        }
    
    def to_post_record(self):
        return   {"fields": {
                "Name": "[DDL] " + self.name,
                "Date": self.date.strftime("%Y-%m-%d"),
                "Ref URL": self.ref_url,
                "Related Work ID": self.related_work_id,
                "Type": self.type   
            },
                "typecast": True}

    

class TodoAssignment(object):
    def __init__(self, name: str, date: datetime, ref_url: str, related_work_id: str):
        self.name = name
        self.date = date
        self.ref_url = ref_url
        # self.id = id
        self.related_work_id = related_work_id
        self.type = "Assignment"

    def to_json(self) -> Dict:
        return{
            "Name": self.name,
            "Date": self.date,
            "Ref URL": self.ref_url,
            # "id": self.id,
            "related assignment id": self.related_work_id,
            "Type": self.type
        }
    
    def to_post_record(self):
        return   {"fields": {
                "Name": self.name,
                "Date": self.date.strftime("%Y-%m-%d"),
                "Ref URL": self.ref_url,
                "Related Work ID": self.related_work_id,
                "Type": self.type   
            },
                "typecast": True}