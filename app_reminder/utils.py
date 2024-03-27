import os
from datetime import datetime

from dotenv import load_dotenv
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


def determine_command(message: str):
    """Определяет тип команды на основе текста сообщения."""
    message = message.lower()
    if "покажи" in message:
        return "show"
    elif "добавь" in message:
        return "add"
    elif "удали" in message:
        return "delete"
    return "unknown"


def parse_command(message):
    """Разбирает команду и извлекает из нее время и текст напоминания."""
    _, time_str, date_str, *reminder_parts = message.split()
    reminder_text = " ".join(reminder_parts)
    try:
        reminder_time = datetime.strptime(
            f"{time_str} {date_str}", "%H:%M %d.%m.%Y"
        )
        return reminder_time, reminder_text
    except ValueError:
        return None, None


async def send_message_via_whatsapp(message: str, to: str):
    """Отправляет сообщение через WhatsApp, используя Twilio API."""
    http_client = AsyncTwilioHttpClient()
    client = Client(ACCOUNT_SID, AUTH_TOKEN, http_client=http_client)
    message_instance = await client.messages.create_async(
        from_=FROM_WHATSAPP_NUMBER, body=message, to=to
    )
    return message_instance.sid
