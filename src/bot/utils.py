import re
from datetime import datetime
from typing import List, Tuple, Union

from celery.result import AsyncResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client

from bot.models import Reminder, RepeatType
from config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_NUM

TWILIO_CLIENT = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


def send_whatsapp_message(user_id: str, reminder_text: str):
    """
    Отправляет сообщение через WhatsApp с помощью Twilio API.

    Параметры:
        user_id (str): Идентификатор пользователя (например, номер телефона), которому отправляется сообщение.
        reminder_text (str): Текст сообщения, которое будет отправлено пользователю.
    """

    TWILIO_CLIENT.messages.create(
        body=reminder_text,
        from_=TWILIO_NUM,
        to=user_id
    )


def parse_reminder_time_and_text(body: str) -> Tuple[datetime, str, RepeatType]:
    """
    Разбирает тело сообщения, чтобы извлечь дату, время, текст напоминания и тип повторения.

    :param body: Тело сообщения с напоминанием, которое может содержать дату, время, текст и тип повторения.

    :return
        Tuple[datetime, str, RepeatType]:
            - reminder_time (datetime): Время и дата напоминания.
            - reminder_text (str): Текст напоминания.
            - repeat_type (RepeatType): Тип повторения (none, daily, weekly).
    """

    body = body.strip().lower()
    repeat_type = RepeatType.NONE

    if "daily" in body:
        repeat_type = RepeatType.DAILY
        body = body.replace("daily", "").strip()
    elif "weekly" in body:
        repeat_type = RepeatType.WEEKLY
        body = body.replace("weekly", "").strip()

    match = re.search(r"(\d{2}\.\d{2}\.\d{4})\s*(\d{2}:\d{2})", body)

    date_time_str = f"{match.group(1)} {match.group(2)}"
    date_time_str = date_time_str.strip()

    reminder_time = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")

    reminder_text = body.replace(date_time_str, "").strip()

    return reminder_time, reminder_text, repeat_type


async def get_reminders_list(db: AsyncSession, user_id: str) -> Union[str, List[str]]:
    """
    Получает список всех активных напоминаний для заданного пользователя.

    :param db: Объект сессии базы данных для выполнения запроса.
    :param  user_id: Идентификатор пользователя, для которого запрашиваются напоминания.

    :return
        Union[str, List[str]]:
            - Если напоминаний нет, возвращает строку "You have no reminders".
            - Если напоминания есть, возвращает список напоминаний.
    """

    result = await db.execute(select(Reminder).
                              filter(Reminder.user_id == user_id).
                              where(Reminder.reminder_time > datetime.now())
                              )
    reminders = result.scalars().all()

    if not reminders:
        return "You have no reminders"

    reminder_list = []
    for reminder in reminders:
        reminder_list.append(f"Reminder {reminder.id}. {reminder.message} at "
                             f"{reminder.reminder_time.strftime('%d.%m.%Y %H:%M')}")

    return "\n".join(reminder_list)


async def delete_reminder(db: AsyncSession, user_id: str, reminder_id: int) -> str:
    """
    Удаляет напоминание из базы данных и отменяет связанную задачу Celery.

    :param db: Объект сессии базы данных для выполнения запроса.
    :param user_id: Идентификатор пользователя, который хочет удалить напоминание.
    :param reminder_id: Идентификатор напоминания, которое нужно удалить.

    :return
        str: Сообщение о результате операции.
    """

    result = await db.execute(select(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ))
    reminder = result.scalar_one_or_none()

    if reminder is None:
        return "Reminder not found"

    if reminder.task_id:
        task = AsyncResult(reminder.task_id)
        task.revoke(terminate=True)

    await db.delete(reminder)
    await db.commit()
    return f"Reminder {reminder_id} deleted successfully"
