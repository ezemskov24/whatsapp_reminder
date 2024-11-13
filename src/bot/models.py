from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, Enum

from database.db_connection import Base


class RepeatType(PyEnum):
    """
    Перечисление для типов повторений напоминаний.

    Attributes:
        NONE (str): Без повторения (напоминание только один раз).
        DAILY (str): Ежедневное напоминание.
        WEEKLY (str): Еженедельное напоминание.
    """
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


class Reminder(Base):
    """
    Модель для таблицы `reminder`, которая хранит информацию о напоминаниях в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор напоминания.
        user_id (str): Идентификатор пользователя (номер телефона).
        reminder_time (datetime): Время, когда должно быть отправлено напоминание.
        message (str): Текст напоминания.
        created_at (datetime): Время создания напоминания.
        task_id (str): Идентификатор задачи в Celery.
        repeat_type (RepeatType): Тип повторения напоминания.
    """
    __tablename__ = "reminder"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    reminder_time = Column(DateTime)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    task_id = Column(String)
    repeat_type = Column(Enum(RepeatType), default=RepeatType.NONE)

    def __repr__(self):
        return (
            f"Reminder("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"reminder_time={self.reminder_time}, "
            f"message={self.message}, "
            f"repeat_type={self.repeat_type})"
                )
