from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from constants import (
    HELLO,
    INVALID_DELETE_COMMAND_FORMAT_MESSAGE,
    INVALID_TIME_FORMAT_MESSAGE,
    NO_REMINDERS_MESSAGE,
    REMINDER_DELETED_MESSAGE,
    REMINDER_NOT_FOUND_MESSAGE,
)
from models import Reminder, User
from utils import parse_command, send_message_via_whatsapp

scheduler = AsyncIOScheduler()
scheduler.start()


async def find_or_create_user(phone_number: str, db: AsyncSession):
    """Находит пользователя по номеру телефона в базе данных."""
    query = select(User).where(User.phone_number == phone_number)
    result = await db.execute(query)
    user = result.scalars().first()
    sent_welcome_message = False

    if not user:
        new_user = User(phone_number=phone_number, welcomed=True)
        db.add(new_user)
        await db.commit()
        user = new_user
        await send_message_via_whatsapp(HELLO, phone_number)
        sent_welcome_message = True

    elif not user.welcomed:
        user.welcomed = True
        await db.commit()
        await send_message_via_whatsapp(HELLO, phone_number)
        sent_welcome_message = True

    return user, sent_welcome_message


async def handle_show_command(user, db):
    """Обрабатывает команду "покажи", возвращая список напоминаний."""
    query = select(Reminder).where(
        Reminder.user_id == user.id, Reminder.time > datetime.now()
    )
    result = await db.execute(query)
    reminders = result.scalars().all()

    if reminders:
        return "\n".join(
            [
                f"{reminder.time.strftime('%H:%M %d.%m.%Y')} "
                f"{reminder.message}"
                for reminder in reminders
            ]
        )
    else:
        return NO_REMINDERS_MESSAGE


async def handle_add_command(message, user, db, From):
    """Обрабатывает команду "добавь", добавляя новое напоминание."""
    time, reminder_text = parse_command(message)
    if time and time > datetime.now():
        new_reminder = Reminder(
            time=time, message=reminder_text, user_id=user.id
        )
        db.add(new_reminder)
        await db.commit()
        scheduler.add_job(
            send_message_via_whatsapp,
            trigger=DateTrigger(run_date=time),
            args=[reminder_text, From],
        )
        return f"Напоминание '{reminder_text}' создано на {time}."
    else:
        return INVALID_TIME_FORMAT_MESSAGE


async def handle_delete_command(message, user, db):
    """Обрабатывает команду "удали", удаляя указанное напоминание."""
    reminder_time, reminder_text = parse_command(message)
    if reminder_time:
        query = select(Reminder).where(
            Reminder.time == reminder_time,
            Reminder.message == reminder_text,
            Reminder.user_id == user.id,
        )
        reminder = (await db.execute(query)).scalars().first()
        if reminder:
            await db.delete(reminder)
            await db.commit()
            return REMINDER_DELETED_MESSAGE
        else:
            return REMINDER_NOT_FOUND_MESSAGE
    else:
        return INVALID_DELETE_COMMAND_FORMAT_MESSAGE
