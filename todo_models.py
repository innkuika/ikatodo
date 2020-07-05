from typing import Dict

class TodoAssignment(object):
    def __init__(self, name: str, date: str, ref_url: str):
        self.name = name
        self.date = date
        self.ref_url = ref_url

    def to_json(self) -> Dict:
        return{
            "Name": self.name,
            "Date": self.date,
            "Ref URL": self.ref_url
        }
        