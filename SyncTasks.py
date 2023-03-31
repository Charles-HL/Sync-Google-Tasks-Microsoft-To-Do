"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""

import pytz
import logging

from googletask.GoogleTasksApi import GoogleTasksApi
from googletask.entities.GoogleTaskItem import GoogleTaskItem
from googletask.entities.GoogleTaskList import GoogleTaskList
from googletask.entities.GoogleTaskListItem import GoogleTaskListItem
from googletask.entities.GoogleTaskLists import GoogleTaskLists
from microsofttodo.MicrosoftToDoApi import MicrosoftToDoApi
from microsofttodo.entities.MicrosoftTodoListItem import MicrosoftTodoListItem
from microsofttodo.entities.MicrosoftTodoLists import MicrosoftTodoLists
from microsofttodo.entities.MicrosoftTodoTask import MicrosoftTodoTask
from microsofttodo.entities.MicrosoftTodoTaskList import MicrosoftTodoTaskList
from dateutil import parser
from datetime import datetime, timedelta


class SyncTasks:
    """
    Class to sync the tasks from Google Tasks to Microsoft To Do
    """

    def __init__(self, azure_config: dict, google_config: dict):
        self.logger = logging.getLogger('my_logger')
        self.google_tasks_api = GoogleTasksApi(google_config)
        self.microsoft_todo_api = MicrosoftToDoApi(azure_config)

    def sync(self):
        """
        Sync the tasks from Google Tasks to Microsoft To Do
        """
        google_task_lists: GoogleTaskLists = self.google_tasks_api.get_all_lists()
        microsoft_task_lists: MicrosoftTodoLists = self.microsoft_todo_api.get_all_lists()
        # compare default lists
        self._compare_and_update(google_task_lists.task_lists[0], microsoft_task_lists.lists[0])

        # TODO add compare for other lists by name

    def _compare_and_update(self, google_task_list: GoogleTaskListItem, microsoft_task_list: MicrosoftTodoListItem):
        """
        Compare the tasks from the two lists and update the tasks
        :param google_task_list: Google Task List
        :param microsoft_task_list: Microsoft To Do List
        """
        # get all tasks from the list
        google_tasks: GoogleTaskList = self.google_tasks_api.get_all_tasks_from_list(google_task_list.id)
        microsoft_tasks: MicrosoftTodoTaskList = self.microsoft_todo_api.get_all_tasks_from_list(microsoft_task_list.
                                                                                                 item_id)
        # create a list of tasks to update and a list of tasks to create
        google_tasks_to_update: GoogleTaskList = GoogleTaskList(None)
        google_tasks_to_create: GoogleTaskList = GoogleTaskList(None)

        # compare tasks
        for microsoft_task in microsoft_tasks.tasks:
            task_found = False
            for google_task in google_tasks.tasks:
                if google_task.title == microsoft_task.title:
                    task_found = True
                    # check if the task is the same
                    if not SyncTasks.is_same_task(google_task, microsoft_task):
                        # check if the microsoft task is more recent
                        if parser.parse(google_task.updated) < parser.parse(microsoft_task.last_modified_date_time):
                            # update the task
                            notes = None
                            if microsoft_task.body is not None and microsoft_task.body['contentType'] == 'text' and \
                                    microsoft_task.body['content'] is not None:
                                notes = microsoft_task.body['content']
                            google_task_to_update: GoogleTaskItem = google_task
                            google_task_to_update.notes = notes
                            google_task_to_update.status = SyncTasks.microsoft_status_to_google(microsoft_task.status)
                            google_task_to_update.due = SyncTasks.convert_datetime_microsoft_to_google(
                                microsoft_task.due_date_time, is_due_date=True)
                            google_task_to_update.title = microsoft_task.title
                            google_tasks_to_update.tasks.append(google_task_to_update)
                    break
            if task_found is False:
                google_task_to_create: GoogleTaskItem = GoogleTaskItem(title=microsoft_task.title,
                                                                       notes= (microsoft_task.body['content'] if microsoft_task.body is not None and microsoft_task.body['contentType'] == 'text' else None),
                                                                       status=SyncTasks.microsoft_status_to_google(
                                                                           microsoft_task.status),
                                                                       due=SyncTasks.convert_datetime_microsoft_to_google(
                                                                           microsoft_task.due_date_time, is_due_date=True),
                                                                       kind='tasks#task')
                google_tasks_to_create.tasks.append(google_task_to_create)

        microsoft_tasks_to_update: MicrosoftTodoTaskList = MicrosoftTodoTaskList(None)
        microsoft_tasks_to_create: MicrosoftTodoTaskList = MicrosoftTodoTaskList(None)

        for google_task in google_tasks.tasks:
            task_found = False
            for microsoft_task in microsoft_tasks.tasks:
                if google_task.title == microsoft_task.title:
                    task_found = True
                    # check if the task is the same
                    if not SyncTasks.is_same_task(google_task, microsoft_task):
                        # check if the Google task is more recent
                        if parser.parse(google_task.updated) >= parser.parse(microsoft_task.last_modified_date_time):
                            # update the task
                            microsoft_task_to_update: MicrosoftTodoTask = microsoft_task
                            microsoft_task_to_update.title = google_task.title
                            microsoft_task_to_update.body = {'contentType': 'text', 'content': google_task.notes}
                            microsoft_task_to_update.status = SyncTasks.google_status_to_microsoft(google_task.status)
                            microsoft_task_to_update.due_date_time = SyncTasks.convert_datetime_google_to_microsoft(google_task.due)
                            microsoft_tasks_to_update.tasks.append(microsoft_task_to_update)
                    break
            if task_found is False:
                microsoft_task_to_create: MicrosoftTodoTask = MicrosoftTodoTask(title=google_task.title,
                                                                                body={
                                                                                    'contentType': 'text',
                                                                                    'content': google_task.notes
                                                                                },
                                                                                status=SyncTasks.google_status_to_microsoft(
                                                                                    google_task.status),
                                                                                due_date_time=SyncTasks.convert_datetime_google_to_microsoft(
                                                                                    google_task.due))
                microsoft_tasks_to_create.tasks.append(microsoft_task_to_create)

        # update tasks
        for microsoft_task in microsoft_tasks_to_update.tasks:
            self.logger.info("Updating task: " + microsoft_task.title + " to Microsoft")
            self.microsoft_todo_api.update_task(microsoft_task_list.item_id, microsoft_task.id, microsoft_task.to_dict())

        for google_task in google_tasks_to_update.tasks:
            self.logger.info("Updating task: " + google_task.title + " to Google")
            self.google_tasks_api.update_task(google_task_list.id, google_task.id, google_task.to_dict())

        # create tasks
        for microsoft_task in microsoft_tasks_to_create.tasks:
            self.logger.info("Creating task: " + microsoft_task.title + " to Microsoft")
            self.microsoft_todo_api.post_task(microsoft_task_list.item_id, microsoft_task.to_dict())

        for google_task in google_tasks_to_create.tasks:
            self.logger.info("Creating task: " + google_task.title + " to Google")
            self.google_tasks_api.post_task(google_task_list.id, google_task.to_dict())

    @staticmethod
    def is_same_task(task1, task2):
        """
        Checks if two task objects are the same by comparing their common attributes.
        :param task1: The first task object.
        :param task2: The second task object.
        """
        if isinstance(task1, GoogleTaskItem) and isinstance(task2, MicrosoftTodoTask):
            # only compare the common attributes
            return (task1.title == task2.title
                    and (task1.notes == task2.body['content'] or (task1.notes is None and task2.body['content'] == '')
                         if task2.body is not None and task2.body['contentType'] == 'text' else False)
                    and SyncTasks.google_status_to_microsoft(task1.status) == task2.status
                    and (SyncTasks.convert_google_datetime_to_datetime_obj(task1.due) == SyncTasks.convert_microsoft_datetime_to_datetime_obj(task2.due_date_time)))
        elif isinstance(task1, MicrosoftTodoTask) and isinstance(task2, GoogleTaskItem):
            # only compare the common attributes
            return (task1.title == task2.title
                    and (task1.body['content'] == task2.notes or (task1.notes is None and task2.body['content'] == '')
                         if task1.body is not None and task1.body['contentType'] == 'text' else False)
                    and SyncTasks.google_status_to_microsoft(task2.status) == task1.status
                    and (SyncTasks.convert_google_datetime_to_datetime_obj(task2.due) == SyncTasks.convert_microsoft_datetime_to_datetime_obj(task1.due_date_time)))
        else:
            return False

    @staticmethod
    def google_status_to_microsoft(google_status):
        """
        Converts the status of a task from Google to Microsoft.
        :param google_status: The status of the task in Google.
        """
        if google_status == 'needsAction':
            return 'notStarted'
        elif google_status == 'completed':
            return 'completed'
        else:
            return 'notStarted'

    @staticmethod
    def microsoft_status_to_google(microsoft_status):
        """
        Converts the status of a task from Microsoft to Google.
        :param microsoft_status: The status of the task in Microsoft.
        """
        if microsoft_status == 'notStarted':
            return 'needsAction'
        elif microsoft_status == 'completed':
            return 'completed'
        else:
            return 'needsAction'

    @staticmethod
    def convert_datetime_microsoft_to_google(microsoft_datetime, is_due_date=False):
        """
        Converts the datetime of a task from Microsoft to Google.
        :param microsoft_datetime: The datetime of the task in Microsoft.
        """
        if microsoft_datetime is None or microsoft_datetime["dateTime"] is None or microsoft_datetime[
            "timeZone"] is None:
            return None
        else:
            datetime_obj = SyncTasks.convert_microsoft_datetime_to_datetime_obj(microsoft_datetime)

            if is_due_date:
                # get the nearest date at midnight because google api does not support timezones and times in the due
                datetime_gg = SyncTasks.get_nearest_date_at_midnight(datetime_obj)
            else:
                # Convert the datetime object to UTC timezone
                datetime_gg = datetime_obj.astimezone(pytz.utc)

            # Convert the datetime object to the desired format
            datetime_formatted_str = datetime_gg.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            return datetime_formatted_str

    @staticmethod
    def convert_microsoft_datetime_to_datetime_obj(microsoft_datetime):
        """
        Converts the datetime of a task from Microsoft to a datetime object.
        :param microsoft_datetime: The datetime of the task in Microsoft.
        """
        if microsoft_datetime is None or microsoft_datetime["dateTime"] is None or microsoft_datetime[
            "timeZone"] is None:
            return None
        datetime_str = microsoft_datetime["dateTime"]
        timezone_str = microsoft_datetime["timeZone"]
        # Convert the datetime string to a datetime object
        datetime_obj = parser.parse(datetime_str+" "+timezone_str)
        # Get the timezone object from timezone string
        timezone_obj = pytz.timezone(timezone_str)
        # Set the timezone of the datetime object
        datetime_obj = datetime_obj.replace(tzinfo=timezone_obj)
        return datetime_obj

    @staticmethod
    def convert_datetime_google_to_microsoft(due):
        """
        Converts the datetime of a task from Google to Microsoft.
        :param due: The datetime of the task in Google.
        """
        if due is None:
            return None
        else:
            input_datetime_obj = SyncTasks.convert_google_datetime_to_datetime_obj(due)
            # create the required output string
            output_datetime_str = input_datetime_obj.strftime('%Y-%m-%dT%H:%M:%S.%f')
            output_timezone_str = 'UTC'
            output_dict = {'dateTime': output_datetime_str, 'timeZone': output_timezone_str}
            return output_dict

    @staticmethod
    def convert_google_datetime_to_datetime_obj(due):
        """
        Converts the datetime of a task from Google to a datetime object.
        :param due: The datetime of the task in Google.
        """
        if due is None:
            return None
        # convert the string to datetime object
        input_datetime_obj = parser.parse(due)
        return input_datetime_obj

    @staticmethod
    def get_nearest_date_at_midnight(dt):
        if dt.hour < 12:
            # If the hour is less than 12, set the time to 00:00
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # If the hour is greater than or equal to 12, set the time to 23:59:59.999999
            return (dt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
