"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
from googletask.entities.GoogleTaskItem import GoogleTaskItem
from typing import List


class GoogleTaskList:
    def __init__(self, json_data):
        self.tasks: List[GoogleTaskItem] = []
        if json_data is not None:
            for task_dict in json_data:
                self.tasks.append(GoogleTaskItem(task_dict))
