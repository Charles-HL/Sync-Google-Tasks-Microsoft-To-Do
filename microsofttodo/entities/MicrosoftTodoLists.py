"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
from microsofttodo.entities.MicrosoftTodoListItem import MicrosoftTodoListItem


class MicrosoftTodoLists:
    def __init__(self, json_data):
        self.context = json_data['@odata.context']
        self.lists = []
        for item in json_data['value']:
            todo_list_item = MicrosoftTodoListItem(item['@odata.etag'], item['displayName'], item['isOwner'],
                                                   item['isShared'],
                                                   item['wellknownListName'], item['id'])
            self.lists.append(todo_list_item)
