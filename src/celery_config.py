import os
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    __name__,
    broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
)

import bot.tasks

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_scheduler='celery.beat:PersistentScheduler',
    beat_schedule_filename='celerybeat-schedule',
)
