from metastore import Metastore
from work_models import Assignment

class Metacache(object):
    def __init___(self, metastore: Metastore):
        self.metastore = metastore

    def get_assignment_id(self) -> str:
        pass
    
    def get_assignment_by_id(self) -> Assignment:
        pass