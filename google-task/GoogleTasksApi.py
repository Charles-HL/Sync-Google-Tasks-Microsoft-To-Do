import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']


class GoogleTaskList:
    def __init__(self, json_data):
        self.tasks = []
        for task_dict in json_data:
            self.tasks.append(GoogleTaskItem(task_dict))


class GoogleTaskItem:
    def __init__(self, task_dict):
        self.kind = task_dict.get('kind')
        self.id = task_dict.get('id')
        self.etag = task_dict.get('etag')
        self.title = task_dict.get('title')
        self.updated = task_dict.get('updated')
        self.selfLink = task_dict.get('selfLink')
        self.position = task_dict.get('position')
        self.notes = task_dict.get('notes')
        self.status = task_dict.get('status')
        self.links = task_dict.get('links')
        self.due = task_dict.get('due')
        self.completed = task_dict.get('completed')
        self.deleted = task_dict.get('deleted')
        self.parent = task_dict.get('parent')
        self.hidden = task_dict.get('hidden')


class GoogleTaskListItem:
    def __init__(self, task_list_id, title, updated):
        self.id = task_list_id
        self.title = title
        self.updated = updated


class GoogleTaskLists:
    def __init__(self, json_data):
        self.data = json_data
        self.task_lists = []
        self.parse_data()

    def parse_data(self):
        for item in self.data:
            if item['kind'] == 'tasks#taskList':
                task_list = GoogleTaskListItem(
                    task_list_id=item['id'],
                    title=item['title'],
                    updated=item['updated']
                )
                self.task_lists.append(task_list)

    def get_task_lists(self):
        return self.task_lists

    def get_task_list_by_id(self, task_list_id):
        for task_list in self.task_lists:
            if task_list['id'] == task_list_id:
                return task_list

        return None


class GoogleTasksApi:
    def __init__(self):
        self.cred = None
        self._update_cred()

    def _update_cred(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.cred = creds

    def get_task_lists(self):
        try:
            service = build('tasks', 'v1', credentials=self.cred)
            result = service.tasklists().list(maxResults=999).execute()
            items = result.get('items', [])
            return GoogleTaskLists(items)
        except HttpError as err:
            print(err)
            return None

    def get_task_list(self, task_list_id):
        try:
            service = build('tasks', 'v1', credentials=self.cred)
            result = service.tasks().list(tasklist="@default", showDeleted=True, showHidden=True,
                                          showCompleted=True).execute()
            tasks = result.get("items", [])
            return GoogleTaskList(tasks)
        except HttpError as err:
            print(err)
            return None


if __name__ == '__main__':
    api = GoogleTasksApi()
    print(api.get_task_lists().task_lists[0].title)
    print(api.get_task_list(api.get_task_lists().task_lists[0].id).tasks[0].title)
