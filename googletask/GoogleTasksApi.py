"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
import configparser
import json
import os.path
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from googletask.entities.GoogleTaskItem import GoogleTaskItem
from googletask.entities.GoogleTaskList import GoogleTaskList
from googletask.entities.GoogleTaskLists import GoogleTaskLists

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']


class GoogleTasksApi:

    def __init__(self, google_settings: dict):
        self.settings = google_settings
        self.logger = logging.getLogger('my_logger')
        # get the path of the current file
        self.file_path = os.path.abspath(__file__)
        # get the directory path of the current file
        self.dir_path = os.path.dirname(self.file_path)
        self.cred = None
        self._update_cred()

    def _update_cred(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path = os.path.join(self.dir_path, 'token.json')
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(json.loads(self.settings["credentials"]), SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.cred = creds

    def get_all_lists(self):
        try:
            service = build('tasks', 'v1', credentials=self.cred)
            result = service.tasklists().list(maxResults=99999).execute()
            items = result.get('items', [])
            return GoogleTaskLists(items)
        except HttpError as err:
            self.logger.info(err)
            return None

    def get_all_tasks_from_list(self, task_list_id):
        try:
            service = build('tasks', 'v1', credentials=self.cred)
            result = service.tasks().list(tasklist=task_list_id, showDeleted=False, showHidden=True,
                                          showCompleted=True, maxResults=99999).execute()
            tasks = result.get("items", [])
            return GoogleTaskList(tasks)
        except HttpError as err:
            self.logger.info(err)
            return None

    def post_task(self, task_list_id, task):
        try:
            service = build('tasks', 'v1', credentials=self.cred)
            result = service.tasks().insert(tasklist=task_list_id, body=task).execute()
            return result
        except HttpError as err:
            self.logger.error(err)
            return None

    def update_task(self, task_list_id, task_id, task):
        try:
            service = build('tasks', 'v1', credentials=self.cred)
            result = service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()
            return result
        except HttpError as err:
            self.logger.error(err)
            return None