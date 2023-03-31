"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
import configparser
import logging
import datetime
import os
import threading
import time
import requests
from azure.identity import DeviceCodeCredential
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider)
from msgraph import GraphRequestAdapter, GraphServiceClient
from azure.core.credentials import AccessToken
from microsofttodo.entities.MicrosoftTodoLists import MicrosoftTodoLists
from microsofttodo.entities.MicrosoftTodoTask import MicrosoftTodoTask
from microsofttodo.entities.MicrosoftTodoTaskList import MicrosoftTodoTaskList


class MicrosoftToDoApi:
    access_token = None
    device_code_credential = None
    auth_provider = None
    adapter = None
    user_client = None
    token_refresh_thread = None
    settings = None

    def __init__(self, azure_config: dict):
        self.logger = logging.getLogger('my_logger')
        self.settings = azure_config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')
        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        self.auth_provider = AzureIdentityAuthenticationProvider(self.device_code_credential, scopes=graph_scopes)
        self.adapter = GraphRequestAdapter(self.auth_provider)
        self.user_client = GraphServiceClient(self.adapter)
        graph_scopes = self.settings['graphUserScopes']

        self.access_token = self.device_code_credential.get_token(graph_scopes)
        self.logger.info("Microsoft token retrieved successfully at {}".format(datetime.datetime.now()))
        self.token_refresh_thread = threading.Thread(target=self.refresh_token, daemon=True)
        self.token_refresh_thread.start()

    def refresh_token(self):
        while True:
            self.logger.info("Microsoft token expires in {} seconds".format(
                self.access_token.expires_on - datetime.datetime.now().timestamp()))
            time.sleep(max(self.access_token.expires_on - datetime.datetime.now().timestamp() - 300, 0))
            try:
                graph_scopes = self.settings['graphUserScopes']
                token = self.device_code_credential.get_token(graph_scopes)
                self.access_token = token
                self.logger.info("Microsoft token refreshed successfully at {}".format(datetime.datetime.now()))
            except Exception as e:
                self.logger.info("Failed to refresh token: {}".format(e))

    def stop_thread(self):
        self.logger.info("Stopping thread...")
        self.token_refresh_thread.join()
        self.logger.info("Thread stopped")

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
        json = response.json()
        if 'error' in json:
            raise Exception(json)
        return MicrosoftTodoLists(json)

    def get_all_tasks_from_list(self, list_id):
        # Set the API endpoint URL
        url = "https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks".format(list_id)
        headers = self._get_request_header()
        # Make the GET API request
        response = requests.get(url, headers=headers)
        json = response.json()
        if 'error' in json:
            raise Exception(json)
        return MicrosoftTodoTaskList(json)

    def post_task(self, list_id, task):
        # Set the API endpoint URL
        url = "https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks".format(list_id)
        headers = self._get_request_header()
        # Make the GET API request
        response = requests.post(url, headers=headers, json=task)
        json = response.json()
        if 'error' in json:
            raise Exception(json)
        return MicrosoftTodoTask(json)

    def update_task(self, list_id, task_id, task):
        # Set the API endpoint URL
        url = "https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}".format(list_id, task_id)
        headers = self._get_request_header()
        # Make the GET API request
        response = requests.patch(url, headers=headers, json=task)
        json = response.json()
        if 'error' in json:
            raise Exception(json)
        return MicrosoftTodoTask(json)