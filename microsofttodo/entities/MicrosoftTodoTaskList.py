"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
from microsofttodo.entities.MicrosoftTodoTask import MicrosoftTodoTask
from typing import List


class MicrosoftTodoTaskList:
    tasks: List[MicrosoftTodoTask] = []

    def __init__(self, data):
        # Extract values from the JSON and create instances of the Task class
        self.tasks = []

        if data is not None:
            for task_json in data['value']:
                if 'completedDateTime' in task_json:
                    completed_date_time = task_json['completedDateTime']
                else:
                    completed_date_time = None
                if 'reminderDateTime' in task_json:
                    reminder_date_time = task_json['reminderDateTime']
                else:
                    reminder_date_time = None

                if 'dueDateTime' in task_json:
                    due_date_time = task_json['dueDateTime']
                else:
                    due_date_time = None

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
                    reminder_date_time=reminder_date_time,
                    due_date_time=due_date_time
                )
                self.tasks.append(task)

            if '@odata.context' in data:
                self.context = data['@odata.context']
            else:
                self.context = None
            if '@odata.nextLink' in data:
                self.next_link = data['@odata.nextLink']
            else:
                self.next_link = None
