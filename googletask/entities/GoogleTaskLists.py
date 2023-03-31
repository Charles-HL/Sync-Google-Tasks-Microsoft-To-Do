"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
from googletask.entities.GoogleTaskListItem import GoogleTaskListItem


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
