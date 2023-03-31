"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
import json


class GoogleTaskItem:
    def __init__(self, task_dict=None, kind=None, id=None, etag=None, title=None, updated=None,
                 self_link=None, position=None, notes=None, status=None, links=None, due=None,
                 completed=None, deleted=None, parent=None, hidden=None):

        if task_dict is not None:
            if not isinstance(task_dict, dict):
                raise ValueError('task_dict must be a dictionary')
            self.kind = task_dict.get('kind')
            self.id = task_dict.get('id')
            self.etag = task_dict.get('etag')
            self.title = task_dict.get('title')
            self.updated = task_dict.get('updated')
            self.self_link = task_dict.get('selfLink')
            self.position = task_dict.get('position')
            self.notes = task_dict.get('notes')
            self.status = task_dict.get('status')
            self.links = task_dict.get('links')
            self.due = task_dict.get('due')
            self.completed = task_dict.get('completed')
            self.deleted = task_dict.get('deleted')
            self.parent = task_dict.get('parent')
            self.hidden = task_dict.get('hidden')
        else:
            self.kind = kind
            self.id = id
            self.etag = etag
            self.title = title
            self.updated = updated
            self.self_link = self_link
            self.position = position
            self.notes = notes
            self.status = status
            self.links = links
            self.due = due
            self.completed = completed
            self.deleted = deleted
            self.parent = parent
            self.hidden = hidden

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        filtered_dict = {k: v for k, v in self.__dict__.items() if v is not None}
        return filtered_dict
