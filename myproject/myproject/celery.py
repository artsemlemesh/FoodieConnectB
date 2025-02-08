import os
# from celery import Celery
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# import tasks.monitoring

app.autodiscover_tasks()
import tasks # also set up import in __init__.py of the tasks folder




#PROBABLY NOT NECESSARY BECAUSE IVE ADDED THIS FUNCITONALITY IN SETTINGS.PY
# from celery import signals
# import logging
# import time

# logger = logging.getLogger('celery')

# @signals.task_prerun.connect
# def task_prerun_handler(sender=None, task_id=None, task=None, args=None, **kwargs):
#     task.start_time = time.time()

# @signals.task_postrun.connect
# def task_postrun_handler(sender=None, task_id=None, task=None, args=None, retval=None, state=None, **kwargs):
#     elapsed_time = time.time() - task.start_time
#     logger.info(f"Task: {sender.name} | State: {state} | Time: {elapsed_time:.2f}s")