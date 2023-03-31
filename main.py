"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""
from SyncTasks import SyncTasks
import time
import logging
from logging.handlers import RotatingFileHandler
import os
import configparser
import threading

INTERVAL_SYNC_IN_MINUTES = 60  # default
LOGGING_LEVEL = logging.DEBUG

# configure the logger
logger = logging.getLogger('my_logger')
logger.setLevel(LOGGING_LEVEL)

# get the path of the current file
file_path = os.path.abspath(__file__)
# get the directory path of the current file
dir_path = os.path.dirname(file_path)

# create a rotating file handler
file_handler = RotatingFileHandler('logs/sync-tasks.log', maxBytes=10 * 1024 * 1024, backupCount=3)
file_handler.setLevel(LOGGING_LEVEL)

# create a stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOGGING_LEVEL)

# create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# set the formatter for both handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# load config
# get the path of the current file
file_path = os.path.abspath(__file__)
# get the directory path of the current file
dir_path = os.path.dirname(file_path)
config = configparser.ConfigParser()
config.read(os.path.join(dir_path, 'config', 'config.cfg'))
azure_settings = config['azure']
google_settings = config['google-api']
sync_settings = config['sync']
if 'syncIntervalInMinute' in sync_settings:
    INTERVAL_SYNC_IN_MINUTES = int(sync_settings['syncIntervalInMinute'])

syncTasks: SyncTasks = SyncTasks(azure_settings, google_settings)


def sync_job():
    while True:
        logger.info('Syncing tasks...')
        syncTasks.sync()
        logger.info('Syncing tasks complete')
        logger.info('Next sync in ' + str(INTERVAL_SYNC_IN_MINUTES) + ' minutes')
        time.sleep(INTERVAL_SYNC_IN_MINUTES * 60)


sync_thread = threading.Thread(target=sync_job, daemon=True)
sync_thread.start()
# Keep the main thread running indefinitely
while True:
    time.sleep(1)
