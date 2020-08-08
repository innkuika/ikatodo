import os


def get_env_or_raise(key: str) -> str:
    if key not in os.environ:
        raise RuntimeError(f"{key} does not exist in environ")
    return os.environ[key]


class GlobalVar(object):
    def __init__(self):
        self.ASSIGNMENTS_URL = get_env_or_raise("ASSIGNMENTS_AIRTABLE_API")
        self.TODO_URL = get_env_or_raise("TODOS_AIRTABLE_API")
        self.OH_URL = get_env_or_raise("OFFICE_HOUR_AIRTABLE_API")
        self.HEADERS = {'Authorization': f"Bearer {get_env_or_raise('AUTH_TOKEN')}",
                        'Content-Type': 'application/json'}
