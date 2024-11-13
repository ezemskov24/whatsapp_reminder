from datetime import datetime, timedelta

from sqlalchemy import select

from bot.models import Reminder, RepeatType
from celery_config import celery_app
from bot.utils import send_whatsapp_message
from database.db_connection import get_db


@celery_app.task
def send_reminder_task(user_id: str, reminder_text: str, reminder_time: str):
    """
    Отправляет напоминание через WhatsApp.

    :param user_id: Идентификатор пользователя
    :param reminder_text: Текст напоминания
    :param reminder_time: Время напоминания в формате 'dd.mm.yyyy HH:MM'
    """
    send_whatsapp_message(user_id, reminder_text)


@celery_app.task
async def send_daily_reminders():
    """
    Отправляет ежедневные напоминания в заданное время.
    Эта задача выполняется ежедневно и проверяет все напоминания с типом 'DAILY'.
    """
    async with get_db() as db:
        reminders = await db.execute(
            select(Reminder).filter(Reminder.repeat_type == RepeatType.DAILY)
        )
        now = datetime.now()
        for reminder in reminders.scalars().all():
            reminder_time = reminder.reminder_time.replace(year=now.year, month=now.month, day=now.day)
            delay_seconds = (reminder_time - now).total_seconds()

            if delay_seconds < 0:
                reminder_time = reminder_time.replace(day=now.day + 1)  # на следующий день
                delay_seconds = (reminder_time - now).total_seconds()

            send_reminder_task.apply_async(
                args=[reminder.user_id, reminder.message, reminder.reminder_time.strftime("%d.%m.%Y %H:%M")],
                countdown=delay_seconds
            )

@celery_app.task
async def send_weekly_reminders():
    """
    Отправляет еженедельные напоминания в заданное время.
    Эта задача выполняется каждую неделю и проверяет все напоминания с типом 'WEEKLY'.

    """
    async with get_db() as db:
        reminders = await db.execute(
            select(Reminder).filter(Reminder.repeat_type == RepeatType.WEEKLY)
        )
        for reminder in reminders.scalars().all():
            if reminder.reminder_time.time() == datetime.now().time() and \
               reminder.reminder_time.weekday() == datetime.now().weekday():
                send_whatsapp_message(reminder.user_id, reminder.message)
                next_week_day = datetime.combine(datetime.today() + timedelta(weeks=1), reminder.reminder_time.time())
                delay_seconds = (next_week_day - datetime.now()).total_seconds()
                send_reminder_task.apply_async(
                    args=[reminder.user_id, reminder.message],
                    countdown=delay_seconds
                )
