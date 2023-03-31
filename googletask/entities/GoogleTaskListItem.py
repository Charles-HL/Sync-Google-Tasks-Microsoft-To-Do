"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""


class GoogleTaskListItem:
    def __init__(self, task_list_id, title, updated):
        self.id = task_list_id
        self.title = title
        self.updated = updated
