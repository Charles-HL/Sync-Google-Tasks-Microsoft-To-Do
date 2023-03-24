"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""

import configparser
import io
import json
import os.path
from azure.identity import DeviceCodeCredential
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider)
from msgraph import GraphRequestAdapter, GraphServiceClient
import datetime


def get_token():
    try:
        if os.path.exists('token.json'):
            with io.open('token.json', "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                if datetime.datetime.fromtimestamp(data["expires"]) < datetime.datetime.now():
                    raise Exception('Token expired')
                return data['token']
    except Exception as e:
        # delete the token file
        if os.path.exists('token.json'):
            os.remove('token.json')
        print("Error getting the saved token", e)

    # get a new token
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']
    settings = azure_settings
    client_id = settings['clientId']
    tenant_id = settings['tenantId']
    graph_scopes = settings['graphUserScopes'].split(' ')
    device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
    auth_provider = AzureIdentityAuthenticationProvider(device_code_credential, scopes=graph_scopes)
    adapter = GraphRequestAdapter(auth_provider)
    user_client = GraphServiceClient(adapter)
    graph_scopes = settings['graphUserScopes']
    access_token = device_code_credential.get_token(graph_scopes)

    with open('token.json', 'w') as token:
        token_dict = {"token": access_token.token, "expires": access_token.expires_on}
        token.write(json.dumps(token_dict))

    return access_token
