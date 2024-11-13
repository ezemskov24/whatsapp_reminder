from datetime import datetime

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_connection import get_db
from bot.models import Reminder
from bot.utils import parse_reminder_time_and_text, send_whatsapp_message, get_reminders_list, delete_reminder
from bot.tasks import send_reminder_task

bot_router: APIRouter = APIRouter()

@bot_router.post("/reminder")
async def send_reminder(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Создает напоминание, удаляет его или выводит список всех напоминаний для пользователя.

    - Если в сообщении указана команда "reminders list", выводится список всех напоминаний.
    - Если в сообщении указана команда "delete {id}", то удаляется напоминание с указанным id.
    - Если в сообщении указано время напоминания в формате 'dd.mm.yyyy HH:MM', создается новое напоминание.

    В случае ошибок возвращаются соответствующие сообщения.

    :param request: Объект запроса, содержащий данные от пользователя
    :param db: Подключение к базе данных
    :return: Ответ с информацией о статусе и возможной ошибке
    """
    form = await request.form()
    user_id = form.get("From")
    body = form.get("Body")

    try:
        if body.strip().lower() == "reminders list":
            reminders = await get_reminders_list(db, user_id)
            send_whatsapp_message(user_id, reminders)
            return {"status": "Success", "message": "Reminder list sent to WhatsApp"}

        elif body.lower().startswith("delete"):
            try:
                reminder_id = int(body.split()[1])
                result_message = await delete_reminder(db, user_id, reminder_id)
                send_whatsapp_message(user_id, result_message)
                return {"status": "Success", "message": result_message}

            except (IndexError, ValueError):
                error_message = "Please provide a valid reminder ID in the format 'delete {id}'"
                send_whatsapp_message(user_id, error_message)
                return {"status": "Error", "message": error_message}


        reminder_time, reminder_text, repeat_type = parse_reminder_time_and_text(body)

        delay_seconds = (reminder_time - datetime.now()).total_seconds()
        if delay_seconds < 0:
            send_whatsapp_message(user_id, "Reminder time is in the past. Please set a future time")
            return {"status": "Error", "message": "Reminder time is in the past. Please set a future time"}

        reminder = Reminder(
            user_id=user_id,
            reminder_time=reminder_time,
            message=reminder_text,
            repeat_type=repeat_type,
        )
        db.add(reminder)
        await db.commit()

        task = send_reminder_task.apply_async(
            args=[user_id, reminder_text, reminder_time.strftime("%d.%m.%Y %H:%M")],
            countdown=delay_seconds
        )
        reminder.task_id = task.id
        await db.commit()

        return {
            "status": "Reminder scheduled",
            "reminder_time": reminder_time,
            "message": reminder_text
        }

    except ValueError:
        error_message = "Invalid date and time format. Please use dd.mm.yyyy HH:MM"
        send_whatsapp_message(user_id, error_message)
        return {"status": "Error", "message": error_message}

    except Exception:
        error_message = "Invalid format"
        send_whatsapp_message(user_id, error_message)
        return {"status": "Error", "message": error_message}
