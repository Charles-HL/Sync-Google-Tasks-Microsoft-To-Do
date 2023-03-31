"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
import json
import re


class MicrosoftTodoTask:
    def __init__(self, task_dict=None, etag=None, importance=None, is_reminder_on=None, status=None, title=None,
                 created_date_time=None,
                 last_modified_date_time=None,
                 has_attachments=None, categories=None, id=None, body=None, completed_date_time=None,
                 reminder_date_time=None, due_date_time=None):
        if task_dict is not None:
            if not isinstance(task_dict, dict):
                raise ValueError('task_dict must be a dictionary')
            if 'completedDateTime' in task_dict:
                completed_date_time = task_dict['completedDateTime']
            else:
                completed_date_time = None
            if 'reminderDateTime' in task_dict:
                reminder_date_time = task_dict['reminderDateTime']
            else:
                reminder_date_time = None

            if 'dueDateTime' in task_dict:
                due_date_time = task_dict['dueDateTime']
            else:
                due_date_time = None

            self.etag = task_dict['@odata.etag'],
            self.importance = task_dict['importance'],
            self.is_reminder_on = task_dict['isReminderOn'],
            self.status = task_dict['status'],
            self.title = task_dict['title'],
            self.created_date_time = task_dict['createdDateTime'],
            self.last_modified_date_time = task_dict['lastModifiedDateTime'],
            self.has_attachments = task_dict['hasAttachments'],
            self.categories = task_dict['categories'],
            self.id = task_dict['id'],
            self.body = task_dict['body'],
            self.completed_date_time = completed_date_time,
            self.reminder_date_time = reminder_date_time,
            self.due_date_time = due_date_time

        else:
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
            self.due_date_time = due_date_time

    def to_dict(self):
        # Create a new dictionary with modified keys
        new_dict = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if key == 'etag':
                    new_dict['@odata.etag'] = value
                else:
                    # Remove underscores and capitalize words
                    modified_key = re.sub(r'_([a-zA-Z])', lambda m: m.group(1).upper(), key)
                    new_dict[modified_key] = value
        return new_dict

    def to_json(self):
        # Convert the modified dictionary to a JSON string
        return json.dumps(self.to_dict())
