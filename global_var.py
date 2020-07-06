def init():
    global WORK_URL
    global TODO_URL
    global HEADERS

    WORK_URL = 'https://api.airtable.com/v0/app9aW8jJyqkeNcxP/Assignments'
    TODO_URL = 'https://api.airtable.com/v0/app9aW8jJyqkeNcxP/Todos'
    HEADERS = {'Authorization': "Bearer keyx4zG23QYBXiRXN"}