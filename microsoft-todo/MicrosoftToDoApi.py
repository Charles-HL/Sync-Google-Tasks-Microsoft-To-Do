import configparser
import datetime
import threading
import time
import atexit
import requests
from azure.identity import DeviceCodeCredential
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider)
from msgraph import GraphRequestAdapter, GraphServiceClient
from azure.core.credentials import AccessToken


class MicrosoftTodoListItem:
    def __init__(self, etag, display_name, is_owner, is_shared, wellknown_list_name, item_id):
        self.etag = etag
        self.display_name = display_name
        self.is_owner = is_owner
        self.is_shared = is_shared
        self.wellknown_list_name = wellknown_list_name
        self.item_id = item_id


class MicrosoftTodoLists:
    def __init__(self, json_data):
        self.context = json_data['@odata.context']
        self.lists = []
        for item in json_data['value']:
            todo_list_item = MicrosoftTodoListItem(item['@odata.etag'], item['displayName'], item['isOwner'], item['isShared'],
                                          item['wellknownListName'], item['id'])
            self.lists.append(todo_list_item)


class MicrosoftTodoTask:
    def __init__(self, etag, importance, is_reminder_on, status, title, created_date_time, last_modified_date_time,
                 has_attachments, categories, id, body, completed_date_time, reminder_date_time):
        self.etag = etag
        self.importance = importance
        self.is_reminder_on = is_reminder_on
        self.status = status
        self.title = title
        self.created_date_time = created_date_time
        self.last_modified_date_time = last_modified_date_time
        self.has_attachments = has_attachments
        self.categories = categories
        self.id = id
        self.body = body
        self.completed_date_time = completed_date_time
        self.reminder_date_time = reminder_date_time


class MicrosoftTodoTaskList:
    def __init__(self, data):
        # Extract values from the JSON and create instances of the Task class
        self.tasks = []
        for task_json in data['value']:
            if 'completedDateTime' in task_json:
                completed_date_time = task_json['completedDateTime']
            else:
                completed_date_time = None
            if 'reminderDateTime' in task_json:
                reminder_date_time = task_json['reminderDateTime']
            else:
                reminder_date_time = None
            task = MicrosoftTodoTask(
                etag=task_json['@odata.etag'],
                importance=task_json['importance'],
                is_reminder_on=task_json['isReminderOn'],
                status=task_json['status'],
                title=task_json['title'],
                created_date_time=task_json['createdDateTime'],
                last_modified_date_time=task_json['lastModifiedDateTime'],
                has_attachments=task_json['hasAttachments'],
                categories=task_json['categories'],
                id=task_json['id'],
                body=task_json['body'],
                completed_date_time=completed_date_time,
                reminder_date_time=reminder_date_time
            )
            self.tasks.append(task)
        self.context = data['@odata.context']
        self.next_link = data['@odata.nextLink']


class MicrosoftToDoApi:
    access_token = None
    device_code_credential = None
    auth_provider = None
    adapter = None
    user_client = None
    thread = None
    settings = None

    def __init__(self):
        # get a new token
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        azure_settings = config['azure']
        self.settings = azure_settings
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')
        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        self.auth_provider = AzureIdentityAuthenticationProvider(self.device_code_credential, scopes=graph_scopes)
        self.adapter = GraphRequestAdapter(self.auth_provider)
        self.user_client = GraphServiceClient(self.adapter)
        graph_scopes = self.settings['graphUserScopes']

        self.access_token = self.device_code_credential.get_token(graph_scopes)
        print("Token retrieved successfully at {}".format(datetime.datetime.now()))
        self.thread = threading.Thread(target=self.refresh_token)
        self.thread.start()
        atexit.register(self.stop_thread)

    def refresh_token(self):
        while True:
            print("Token expires in {} seconds".format(
                self.access_token.expires_on - datetime.datetime.now().timestamp()))
            time.sleep(max(self.access_token.expires_on - datetime.datetime.now().timestamp() - 300, 0))
            try:
                graph_scopes = self.settings['graphUserScopes']
                token = self.device_code_credential.get_token(graph_scopes)
                self.access_token = token
                print("Token refreshed successfully at {}".format(datetime.datetime.now()))
            except Exception as e:
                print("Failed to refresh token: {}".format(e))

    def stop_thread(self):
        print("Stopping thread...")
        self.thread.join()
        print("Thread stopped")

    def _get_request_header(self):
        # Set the headers for the API request
        headers = {
            "Authorization": "Bearer " + self.access_token.token,
            "Accept": "application/json"
        }
        return headers

    def get_all_lists(self):
        # Set the API endpoint URL
        url = "https://graph.microsoft.com/v1.0/me/todo/lists"
        headers = self._get_request_header()
        # Make the GET API request
        response = requests.get(url, headers=headers)
        return MicrosoftTodoLists(response.json())

    def get_all_tasks_from_list(self, list_id):
        # Set the API endpoint URL
        url = "https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks".format(list_id)
        headers = self._get_request_header()
        # Make the GET API request
        response = requests.get(url, headers=headers)
        return MicrosoftTodoTaskList(response.json())


if __name__ == '__main__':
    api = MicrosoftToDoApi()
    print(api.get_all_lists().lists[1].display_name)
    print(api.get_all_lists().lists[1].item_id)
    print(api.get_all_tasks_from_list(api.get_all_lists().lists[0].item_id).tasks[5].title)
    print(api.get_all_tasks_from_list(api.get_all_lists().lists[0].item_id).tasks[5].status)
